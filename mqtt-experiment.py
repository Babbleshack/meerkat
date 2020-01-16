import paho.mqtt.client as mqtt
import threading
import time
import json

from itertools import cycle
from random import choice
from datetime import datetime

from key_exchange_helper import *

from Graph import Graph;
from SecurityPolicyDatabase import SecurityPolicyDatabase
from SecurityAsscoiationDatabase import SecurityAssociationDatabase, SecurityAssociation
#from import bcolors
from logger import *

MQTT_ADDR = "127.0.0.1"
MQTT_PORT = 1883

class Server:
    def __init__(self, spd, sad, channel_graph, server_id="key-server"):
        self.spd = spd
        self.sad = sad
        self.channels = channel_graph
        self.id = server_id
        self.mqtt_con = None
        self.message_loop = True

    def connect(self):
        self.mqtt_con = mqtt.Client(self.id)
        self.mqtt_con.on_message = self.on_message
        self.mqtt_con.connect(MQTT_ADDR, MQTT_PORT, keepalive=60, bind_address="")


    def server_loop(self):
        '''
        Starts experiment by creating new sad entry for /*
        '''
        #root_sa = self.sad.create_sa()
        #print_okgreen("Created Root node SA: " + str(root_sa))
        self.mqtt_con.subscribe("#") #subscribe to all
        while self.message_loop:
            self.mqtt_con.loop()
            #print_okblue("Message Loop: " + str(self.message_loop))

    def on_message(self, client_id, userdata, message):
        '''
        Process new message packet
        '''
        print_okblue("---- {}:: Processing Message ---".format(self.id))
        msg = str(message.payload.decode("utf-8"))
        topic = message.topic
        if msg == 'KILL-SIGNAL':
            print_warning("GOT KILL SIGNAL, SETTING MESSAGE_LOOP FLAG TO FALSE")
            self.message_loop = False
        else:
            self.process_message(msg, topic)
        print_okblue("---- {}:: Finished Processing Message ---".format(self.id))

    def process_message(self, msg_json, topic_str):
        '''
        example key request (payload), wrapped by message header
        {
            "client_id": 0,
            "target": "KEY-REQUEST",
            "payload": {
                "target": 3
            }
        }
        '''

        if not msg_json or not topic_str:
            return

        msg = json.loads(msg_json)

        if not validate_msg(msg):
            print_fail("{}::Failed to process message:\n{}".format(self.id, msg_json))
            return

        source_id = msg['source_id']
        payload = msg['payload']
        target = msg['target']

        if source_id == self.id:
            return

        #print_okblue("{} :: Received new valid message:\n{}".format(self.id, msg_json))

        if target == 'KEY-REQUEST':
            self.authenticate_client(source_id, payload, topic_str)
        else:
            print_warning("{} : WARNING: could not process message {}".format(self.id, msg_json))

    def authenticate_client(self, client_id, payload, topic_str):
        '''
        TODO: remove client_id arg
        authenticate a client request, if successful sends response topic
        on by replacing ADVERTISEMENT token with RESPONSE token
        authentication packet = {
            target : "<node-id>",
            client_id : "id of request client"
        }
        '''
        if type(payload) == 'str':
            request = parse_request_packet(payload)
        else:
            request = payload

        if not validate_request_packet(request):
            print_warning("Unable to validate request packet:\n{}".format(str(request)))
            return
        target = request['target']
        sa = None
        #Try to fetch sa for client and target
        sa = self.sad.find_valid_sa(client_id, target)
        if not sa: # NO sa in database, try to create a new one
            print_warning("WARNING:: could not find sa for client" +
                                      " [{}] for target [{}], trying to create one...".format(client_id, target))
        if not sa: # NO sa in database, try to create a new one
            sa  = self.sad.create_sa(client_id, target)

        if not sa:
            print_warning("WARNING:: could not authenticate client" +
                                  " [{}] for target [{}]".format(client_id, target))
            return None
        print_sad(self.sad, "{}-SAD".format(self.id))
        # Send client new key
        rsp_packet = create_response_packet(client_id, target, sa)
        msg_packet = create_msg_packet(self.id, "RESPONSE", rsp_packet, json_encode=True)
        rsp_topic = replace_topic_str(topic_str, "RESPONSE")
        self.mqtt_con.publish(rsp_topic, msg_packet)

    def _replace_topic_str(self, topic_str, new_target, seperator="/"):
        topics = topic_str.split(seperator)
        topics[-1] = new_target
        return seperator.join(topics)

    def loop(self):
        print("loop")
        if self.mqtt_con:
            while True:
                self.mqtt_con.loop()
        print("error")

    def time_loop(self, timeout=3):
        seconds = 0
        while(seconds < timeout):
            print("Loop at T={}".format(str(seconds)))
            self.mqtt_con.loop()
            time.sleep(1)
            seconds = seconds + 1

class Client:
    def __init__(self, topic_group, client_id, spd, channel_graph):
        print("Creating client: " + str(client_id))
        self.topic_group = topic_group
        self.id = client_id
        self.spd = spd
        self.sad = None
        self.mqtt_con = None
        self.channel_graph = channel_graph
        self.message_loop = True
        self.timestamp = 0 #used for measuring time between random requests

    def connect(self):
        self.sad = SecurityAssociationDatabase(self.spd, self.channel_graph)
        self.mqtt_con = mqtt.Client("Client " + str(self.id))
        self.mqtt_con.on_message = self.on_message
        self.mqtt_con.connect(MQTT_ADDR, MQTT_PORT, keepalive=60, bind_address="")
        self.mqtt_con.subscribe('#')
        #client.connect(MQTT_ADDR, MQTT_PORT)

    def on_message(self, client, userdata, message):
        msg = str(message.payload.decode("utf-8"))
        topic = message.topic
        if msg == 'KILL-SIGNAL':
            self.message_loop = False
        else:
            self.process_message(msg, topic)

    def process_message(self, msg_json, topic_str):
        '''
        example key request (payload), wrapped by message header
        {
            "client_id": 0,
            "target": "KEY-REQUEST",
            "payload": {
                "target": 3
            }
        }
        '''
        if not msg_json or not topic_str:
            return

        msg = json.loads(msg_json)

        if not validate_msg(msg):
            print_fail("Failed to process message: \n" + str(msg_json))
            return

        #print(msg)

        source_id = msg['source_id']
        payload = msg['payload']
        target = msg['target']

        if source_id == self.id:
            return

        print_okblue("Received new valid message:\n{}".format(msg_json))

        if target == 'RESPONSE':
            print_header("{}:: GOT RESPONSE MESSAGE".format(self.id))
            self.handle_authentication_response(source_id, payload, topic_str)
        elif target == 'PUBLISH':
            print_header("{}:: GOT PUBLISH MESSAGE".format(self.id))
            self.rcv_msg(source_id, payload)
        else:
            print_warning("{}:: WARNING: could not process message {}".format(self.id, msg_json))


    def rcv_msg(self, source_id, msg):
        #print_header("{} :: rcv_msg called : {}".format(self.id, msg))
        if not validate_enc_message(msg):
            print_fail(
                "{}::ERROR:: could not validate encrypted message:\n{}".format(self.id, msg))

        topic_id = msg['topic_id']
        key = msg['key']
        payload = msg['payload']
        #check if topic is part of security policy
        sp = self.spd.get_security_policy(self.id)
        sp_keys = sp.keys()
        if not topic_id in sp_keys:
            print_fail("{}:: Topic not in secuirty policy dropping: {}".format(self.id, msg))
            return None
        #check sad for key,
        sa_list = self.sad.key_lookup(topic_id)
        if not sa_list: #find SA
            self.request_sec_asoc(topic_id)
            #print_warning(
            #    "{}:: Could not find SA for {}, making request...".format(self.id, topic_id))
        else: # SA found
            key_found = False
            sec_asoc = None
            for ind, sa in enumerate(sa_list): #find sa with matching key
                if sa.key == key:
                    sec_asoc = sa
                    break
            if not sec_asoc: # remove found sa and request a new one
                self.sad.remove_security_association(sec_asoc)
                print_warning(
                    "Could not find SA (stale keys) for" +
                    " {}, making request...".format(topic_id))
            else:
                print_okgreen("{}::Successfully decrypted message: {}".format(msg, self.id))

    def handle_authentication_response(self, source_id, payload, topic_str):
        response = None
        if type(payload) == 'str':
            response = parse_request_packet(payload)
        else:
            response = payload

        if not response:
            return None

        if not validate_response_packet(response):
            print_fail("WARNING:: Failed to validate response:\n{}".format(response))
            return None

        client_id = payload['client_id']
        target = payload['target']
        path = payload['path']
        key = payload['key']

        sa = SecurityAssociation(target, path, key)
        print_header("[{}]::ADDING NEW SAD ENTRY {}".format(self.id, sa))
        self.sad.add_security_association(target, sa)
        print_sad(self.sad, "{}-SAD".format(self.id))

    def choose_random_topic(self):
        vertices = self.channel_graph.vertices()
        r_node = choice(vertices)
        return r_node

    def random_request(self):
        '''
        Chooses random topic from channel graph
        if sec asoc available, send message using key,
        else request new security association
        '''
        topic_id = self.choose_random_topic()
        sec_asoc = self.sad.find_valid_sa(self.id, topic_id)
        if not sec_asoc:
            self.request_sec_asoc(topic_id)
        else:
            #create new message
            self.send_enc_packet(topic_id, "test-date")


    def request_sec_asoc(self, topic_id):
        ''''
        {
        "client_id" : 0,
        "target" : "KEY-REQUEST",
        "payload" : {
            "target" : 3
            }
        }
        '''

        sa_req = create_request_packet(topic_id, self.id)
        #Create path to target

        topic_str = self.channel_graph.get_topic_str(topic_id)

        req_packet = create_request_packet(topic_id, self.id)
        msg_json = create_msg_packet(self.id, "KEY-REQUEST",req_packet, json_encode=True)
        print_header("Publishing [{}] on topic [{}]".format(msg_json, topic_str))
        self.mqtt_con.publish(topic_str, msg_json)

    def send_enc_packet(self, topic_id, msg, target='PUBLISH'):
        '''
        Send encrypted data packet,
        if key available in sad for topic
        use key, else request new key
        '''
        topic_str = self.channel_graph.get_topic_str(topic_id)
        sec_asoc = self.sad.find_valid_sa(self.id, topic_id)
        if not sec_asoc:
            print_fail("Client::send_enc_packet cannot find security association")
            return
        enc_msg = create_enc_message(topic_id, sec_asoc.key, msg)
        msg = create_msg_packet(self.id, 'PUBLISH', enc_msg, json_encode=True)
        self.mqtt_con.publish(topic_str, msg)

    def start(self):
        self.mqtt_con.subscribe("#")
        #print_fail("ERROR:: Client::start no implementation")

    def loop(self):
        while self.message_loop:
           self.mqtt_con.loop()

    def time_loop(self, timeout=3):
        seconds = 0
        while(seconds < timeout):
            print("Loop at T={}".format(str(seconds)))
            self.mqtt_con.loop()
            time.sleep(1)
            seconds = seconds + 1

    def timed_random_choice(self, interval=1):
        '''
        interval is float value defining the number
        of seconds because random requests
        '''
        c_time = time.time()
        delta_time = c_time - self.timestamp
        if delta_time > interval:
            self.timestamp = time.time()
            self.random_request()

    def random_loop(self):
        start = datetime.now()
        while self.message_loop:
           self.timed_random_choice()
           self.mqtt_con.loop()
           delta = datetime.now() - start
           if delta.seconds > 10:
               self.message_loop = False






#g = Graph(3,2)

#height = int(input("How many levels: "))
height = 3
#children = int(input("Number of children: "))
children = 2
#n_groups = int(input("Number of Groups/Policies: "))
#n_clients = int(input("Number of clients: "))
n_clients = 1

#testbed = input("Random(r)/Manual(m)")

def create_server_worker(server_id, spd, channel_graph):
    print_okblue("--------------{}-STARTING...-------------".format(server_id))
    s_sad = SecurityAssociationDatabase(spd, channel_graph)
    server = Server(spd, s_sad, channel_graph, 'key-server')
    server.connect()
    server.server_loop()
    print_okblue("--------------{}-EXIT-------------".format(server_id))
    print_okblue("Server Done, exiting")

def create_client_worker(group, client_id, spd, channel_graph):
    print_okblue("--------------{}-STARTED-----------------".format(client_id))
    #create group
    client = Client(group, client_id, spd, channel_graph)
    client.connect()
    client.start()
    client.random_loop()
    client.mqtt_con.publish("/0", "KILL-SIGNAL")
    print_okblue("Client " + str(client_id) + " Done")
    print_okblue("--------------{}-EXIT-----------------".format(client_id))

## Create channel graph and databases
channel_graph = Graph(height, children)
spd = SecurityPolicyDatabase()
sad = SecurityAssociationDatabase(spd, channel_graph)

#Create groups
client_groups = spd.create_group_r(5, channel_graph)
GROUPS = cycle(client_groups)

print(channel_graph)

root = channel_graph.get_node(0)
all_g = spd.create_group(root, channel_graph)
spd.add_security_policy('client-0',all_g)
#print spd
#start server
server_args = {
    'server_id': 'keyserver',
    'spd' : spd,
    'channel_graph' : channel_graph
}

s_thread = threading.Thread(target=create_server_worker, kwargs=server_args)
s_thread.start()
#print("------------------")
#print("MAIN: Thread started")
#s_thread.join()
#print("STHREAD EXIT")
#print("------------------")

client_args = {
    'spd': spd,
    'channel_graph': channel_graph,
    'client_id': None,
    'group': None
}

client_args['client_id'] = 'client-0'
client_args['group'] = all_g

#spd.add_security_policy('client-0', group)

c_thread = threading.Thread(target=create_client_worker, kwargs=client_args)
c_thread.start()

client_args['client_id'] = 'client-1'
client_args['group'] = GROUPS.__next__()
spd.add_security_policy('client-1',client_args['group'])

print_spd(spd)

print(client_args['group'])
d_thread = threading.Thread(target=create_client_worker, kwargs=client_args)
d_thread.start()

d_thread.join()
c_thread.join()
s_thread.join()

print_okgreen("-------------DONE--------------")


