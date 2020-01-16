#! /usr/bin/env python3

import paho.mqtt.client as mqtt

from Graph import Graph;
from SecurityPolicyDatabase import SecurityPolicyDatabase
from SecurityAsscoiationDatabase import SecurityAssociationDatabase


channel_graph = Graph(3, 2)

print(channel_graph)

print(str(channel_graph.traverse(channel_graph.get_node(1), {})))
print(str(channel_graph.traverse(channel_graph.get_node(2), {})))

#spd = SecurityPolicyDatabase()
#sad = SecurityAssociationDatabase(spd, channel_graph)
#
#client_groups = spd.create_group_r(3, channel_graph)
#print("---- Printing Client Groups ----")
#print(*client_groups, sep='\n')
#for group in client_groups:
#    print(str(group))

#spd.add_security_policy(1, client_groups[0])
#spd.add_security_policy(2, client_groups[1])
#spd.add_security_policy(3, client_groups[2])

#print(spd.get_security_policy(1))
#print(spd.get_security_policy(2))
#print(spd.get_security_policy(3))


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
