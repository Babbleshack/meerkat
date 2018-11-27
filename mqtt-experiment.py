import paho.mqtt.client as mqtt
import threading
import time
import json

from itertools import cycle
from Graph import Graph;
from SecurityPolicyDatabase import SecurityPolicyDatabase
from SecurityAsscoiationDatabase import SecurityAssociationDatabase
from bcolors import bcolors

bcolors = bcolors()

def print_spd(spd):
    print("-----------SPD-------------")
    print("client-id | subgraph")
    for client in spd.security_policy_database:
#        print (str(client) + "--------->")
        print (bcolors.OKBLUE + str(spd.security_policy_database[client]) + bcolors.ENDC)
    print("----END-SPD-------")


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
        #client.connect(MQTT_ADDR, MQTT_PORT)


    def server_loop(self):
        '''
        Starts experiment by creating new sad entry for /*
        '''
        #root_sa = self.sad.create_sa()
        #bcolors.print_okgreen("Created Root node SA: " + str(root_sa))
        self.mqtt_con.subscribe("#") #subscribe to all
        while self.message_loop:
            self.mqtt_con.loop()
            #bcolors.print_okblue("Message Loop: " + str(self.message_loop))

    def on_message(self, client_id, userdata, message):
        bcolors.print_okgreen("Processing Message")
        msg = str(message.payload.decode("utf-8"))
        topic = message.topic
        if msg == 'KILL-SIGNAL':
            bcolors.print_warning("GOT KILL SIGNAL, SETTING MESSAGE_LOOP FLAG TO FALSE")
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
        error = False
        if not msg_json or not topic_str:
            return

        msg = json.loads(msg_json)
        if not 'client_id' in msg:
            bcolors.print_warning("cannot find client id")
            error = True
        #elif not msg['topic_id']:
        #    bcolors.print_warning("Cannot find topid id")
        #    error = True
        elif not 'target' in msg:
            bcolors.print_warning("Cannot find target")
            error = True
        elif not 'payload' in msg:
            bcolors.print_warning("Cannot find message payload")
            error = True

        if error:
            bcolors.print_fail("Failed to process message: \n" + str(msg_json))
            return

        client_id = msg['client_id']
        payload = msg['payload']
        target = msg['target']

        print(client_id)
        print(self.id)
        if client_id == self.id:
            bcolors.print_warning("WARNING: received own message")
            return
        print("--------------")


        bcolors.print_okblue("Received new valid message:\n{}".format(msg_json))

        if target == 'KEY-REQUEST':
            print("TARGET KEY-REQUEST")
            self.authenticate_client(client_id, payload, topic_str)
        else:
            bcolors.print_warning("WARNING: could not process message {}".format(msg_json))

    def authenticate_client(self, client_id, payload, topic_str):
        '''
        authenticate a client request, if successful sends response topic
        on by replacing ADVERTISEMENT token with RESPONSE token
        authentication packet = {
            target : "<node-id>"
        }
        '''
        if type(payload) == 'str':
            request = self._parse_request_packet(payload)
        else:
            request = payload
        if not self._validate_request_packet(request):
            bcolors.print_warning("Unable to validate request packet:\n{}".format(str(request)))
            return
        target = request['target']
        sa = None
        #Try to fetch sa for client and target
        sa = self.sad.find_valid_sa(client_id, target)
        if not sa: # NO sa in database, try to create a new one
            bcolors.print_warning("WARNING:: could not find sa for client" +
                                      " [{}] for target [{}], trying to create one...".format(client_id, target))
        if not sa: # NO sa in database, try to create a new one
            sa  = self.sad.create_sa(client_id, target)

        if not sa:
            bcolors.print_fail("WARNING:: could not authenticate client" +
                                  " [{}] for target [{}]".format(client_id, target))
            return None
        # Send client new key
        sa_packet = self._create_sa_packet(client_id, target, sa)
        msg_packet = self._wrap_packet(self.id, target, sa_packet, json_encode=True)
        rsp_topic = self._replace_topic_str(topic_str, "RESPONSE")
        self.mqtt_con.publish(rsp_topic, msg_packet)

    def _replace_topic_str(self, topic_str, new_target, seperator="/"):
        topics = topic_str.split(seperator)
        topics[-1] = new_target
        return seperator.join(topics)


    def _parse_request_packet(self, request_packet):
        r_packet = None
        try:
            r_packet = json.loads(request_packet)
        except:
            bcolors.print_fail("ERROR: Failed to parse request packet:\n{}".format(request_packet))
        return r_packet


    def _validate_request_packet(self, request_packet):
        valid = True
        if not request_packet['target']:
            valid = False
        return valid

    #def authenticate_client(self, client_id, topic_str, target):
    #    #TODO: error handle =
    #    sa = None
    #    #Try to fetch sa for client and target
    #    sa = self.sad.find_valid_sa(client_id, target)
    #    if not sa: # NO sa in database, try to create a new one
    #        sa  = self.sad.create_sa(client_id, target)
    #    if not sa:
    #        bcolors.print_warning("WARNING:: could not authenticate client" +
    #                              "{} for target {}".format(client_id, target))
    #        return None
    #    # Send client new key
    #    sa_packet = self._create_sa_packet(client_id, target, sa)
    #    msg_packet = self._wrap_packet(client_id, target, sa_packet, json_encode=True)
    #    self.mqtt_con.publish(topic_str, msg_packet)

    def _create_sa_packet(self, client, target, sa, json_encode=False):
        '''
        client_id describs id of client receiving sa
        i.e. target_client
        '''
        sa_packet =  {
            'client_id' : client,
            'target' : target,
            'path' : sa.sub_graph,
            'key' : sa.key
        }
        return json.dumps(sa_packet) if json_encode else sa_packet

    def _wrap_packet(self, client, target, data, json_encode=False):
        packet = {
            'client_id' : client,
            'target' : target,
            'payload': data
        }
        return json.dumps(packet) if json_encode else packet








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

    def connect(self):
        self.sad = SecurityAssociationDatabase(self.spd, self.channel_graph)
        self.mqtt_con = mqtt.Client("Client " + str(self.id))
        self.mqtt_con.on_message = self.on_message
        self.mqtt_con.connect(MQTT_ADDR, MQTT_PORT, keepalive=60, bind_address="")
        self.mqtt_con.subscribe('#')
        #client.connect(MQTT_ADDR, MQTT_PORT)

    def on_message(self, client, userdata, message):
        bcolors.print_okgreen("message received " + str(message.payload.decode("utf-8")))
        bcolors.print_okgreen("message topic=" + message.topic)
        bcolors.print_okgreen("message qos=" + str(message.qos))
        bcolors.print_okgreen("message retain flag=" + str(message.retain))
        bcolors.print_warning("WARNING:: client::on_message no implemented")
        topic = str(message.topic)
        msg = str(message.payload.decode("utf-8"))
        if msg == 'KILL-SIGNAL':
            self.message_loop = False

    def start(self):
        self.mqtt_con.subscribe("#")
        #bcolors.print_fail("ERROR:: Client::start no implementation")

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
    s_sad = SecurityAssociationDatabase(spd, channel_graph)
    server = Server(spd, s_sad, channel_graph, 'key-server')
    server.connect()
    server.server_loop()
    #server.loop()
#    server.time_loop()
    #server.loop()
    bcolors.print_okblue("Server Done, exiting")

def create_client_worker(group, client_id, spd, channel_graph):
    #create group
    client = Client(group, client_id, spd, channel_graph)
    client.connect()
    #client.start()
    client.start()
    client.time_loop(10)
    bcolors.print_okblue("Client " + str(client_id) + " Done")

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
spd.add_security_policy(0,all_g)
#print spd
print_spd(spd)

#start server
server_args = {
    'server_id': 'keyserver',
    'spd' : spd,
    'channel_graph' : channel_graph
}

s_thread = threading.Thread(target=create_server_worker, kwargs=server_args)
s_thread.start()
print("------------------")
print("MAIN: Thread started")
s_thread.join()
print("STHREAD EXIT")
print("------------------")

#workers = []
#client_workers = []
#for c_id in range(n_clients):
#    args = {
#        'group' : GROUPS.__next__(),
#        'client_id' : c_id,
#        'spd' : spd,
#        'channel_graph' : channel_graph
#    }
#    thread = threading.Thread(target=create_client_worker,kwargs=args)
#    #workers.append(threading.Thread(target=create_server_worker)
#    client_workers.append(thread)
#
##Start threads
#for worker in client_workers:
#    worker.start()
#
#for worker in client_workers:
#    worker.join()
#s_thread.join()
bcolors.print_okgreen("-------------DONE--------------")
#(self, spd, sad, channel_graph, server_id="key-server"):
#server = Server(spd, sad, channel_graph)
#server.connect()
#server.loop()



#def on_message(client, userdata, message):
#    time.sleep(1)
#    print("received message =",str(message.payload.decode("utf-8")))
#
#CLIENT_NAME = "test-client"
#MQTT_ADDR = "127.0.0.1"
#MQTT_PORT = 1883
#
#client = mqtt.Client(CLIENT_NAME)
#
#client.on_message = on_message
#
#print("Connecting to broker")
#
#client.connect(MQTT_ADDR, MQTT_PORT, keepalive=60, bind_address="")
#
#client.subscribe("#")
#
#while True:
#    client.loop()
#
#print("---END---")
