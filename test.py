#! /usr/bin/env python3

import paho.mqtt.client as mqtt

from Graph import Graph;
from SecurityPolicyDatabase import SecurityPolicyDatabase
from SecurityAsscoiationDatabase import SecurityAssociationDatabase
from itertools import cycle


#channel_graph = Graph(3, 2)
#
#print(channel_graph)
#
#spd = SecurityPolicyDatabase()
#sad = SecurityAssociationDatabase(spd, channel_graph)
#
#client_groups = spd.create_group_r(3, channel_graph)
#print("---- Printing Client Groups ----")
#print(*client_groups, sep='\n')
#
##for group in client_groups:
##    print(str(group))
#
###Create 4 clients
#print("--- Creating security policies ---")
#spd.add_security_policy(1, client_groups[0])
#spd.add_security_policy(2, client_groups[1])
#spd.add_security_policy(3, client_groups[2])
#spd.add_security_policy(4, client_groups[0])
#spd.add_security_policy(5, client_groups[1])
#spd.add_security_policy(6, client_groups[2])
#
#print("--- print policies ---")
#print(str(spd.get_database()))

height = int(input("How many levels: "))
children = int(input("Number of children: "))
n_groups = int(input("Number of Groups/Policies: "))
n_clients = int(input("Number of clients: "))



channel_graph = Graph(height, children)
spd = SecurityPolicyDatabase()
sad = SecurityAssociationDatabase(spd, channel_graph)
client_groups = spd.create_group_r(n_groups, channel_graph)

groups_cycle = cycle(client_groups)

# Round robin group policy assignment
for client in range(n_clients):
    spd.add_security_policy(client, groups_cycle.__next__())

#print assignments
for client in spd.get_database():
    print(str(client) + " : " + str(spd.get_security_policy(client)))


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
