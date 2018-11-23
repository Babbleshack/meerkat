import paho.mqtt.client as mqtt

import Graph as Graph
import SecurityPolicyDatabase as SecurityPolicyDatabase
import SecurityAssociationDatabase as SecurityAssociationDatabase
import bcolors as bcolors

bcolors = bcolors()


MQTT_ADDR = "127.0.0.1"
MQTT_PORT = 1883

class server:
    def __init__(self, spd, sad, channel_graph, server_id="key-server"):
        self.spd = spd
        self.sad = sad
        self.channels = channel_graph
        self.id = server_id
        self.mqtt_con = None

    def connect(self):
        self.mqtt_con = mqtt.Client(self.id)
        self.mqtt_con = self.on_message
        self.mqtt_con.connect(MQTT_ADDR, MQTT_PORT, keepalive=60, bind_address="")
        #client.connect(MQTT_ADDR, MQTT_PORT)
        self.mqtt_con.subscribe("#")

    def on_message(self):
        bcolors.print_fail("ERROR:: server::on_message no implemented")

    def loop(self):
        if self.mqtt_con:
            self.mqtt_con.loop()





class client:
    def __init__(self, topic_group, client_id, spd):
        self.topic_group = topic_group
        self.id = client_id
        self.spd = spd
        self.sad = None
        self.mqtt_con = None

    def connect(self):
        self.sad = SecurityAssociationDatabase(self.spd)
        self.mqtt_con = mqtt.Client(self.id)
        self.mqtt_con.connect(MQTT_ADDR, MQTT_PORT, keepalive=60, bind_address="")
        #client.connect(MQTT_ADDR, MQTT_PORT)

    def on_message(self):
        bcolors.print_fail("ERROR:: server::on_message no implemented")



#g = Graph(3,2)

height = int(input("How many levels: "))
#children = int(input("Number of children: "))
children = 2
n_groups = int(input("Number of Groups/Policies: "))
n_clients = int(input("Number of clients: "))

#testbed = input("Random(r)/Manual(m)")

channel_graph = Graph(height, children)
spd = SecurityPolicyDatabase()
sad = SecurityAssociationDatabase(spd, channel_graph)

    #(self, spd, sad, channel_graph, server_id="key-server"):
server = Server(spd, sad, channel_graph)
server.connect()



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
