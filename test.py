#! /usr/bin/env python3

import paho.mqtt.client as mqtt
import sys
import json

from Graph import Graph;
from SecurityPolicyDatabase import SecurityPolicyDatabase
from SecurityAsscoiationDatabase import SecurityAssociationDatabase
from itertools import cycle
from random import randrange, choice
import sys, getopt

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''


INTERACTIVE = False
TEST = False
TESTBED = False
argv = sys.argv[1::]
if argv:
    if '-i' in argv:
        INTERACTIVE = True
    if '-t' in argv:
        TEST = True
    if '-tb' in argv:
        TESTBED = True

if argv and argv[0] == '-i':
    interactive = True

if INTERACTIVE:
    height = int(input("How many levels: "))
    #children = int(input("Number of children: "))
    children = 2
    n_groups = int(input("Number of Groups/Policies: "))
    n_clients = int(input("Number of clients: "))
elif TESTBED:
    height = 3
    children = 2
    n_groups = 3
    n_clients = 6
else:
    height = 5
    children = 2
    n_groups = 8
    n_clients = 6

channel_graph = Graph(height, children)
spd = SecurityPolicyDatabase()
sad = SecurityAssociationDatabase(spd, channel_graph)
client_id = 5

def print_spd(spd):
    print("-----------SPD-------------")
    print("client-id | subgraph")
    for client in spd.security_policy_database:
#        print (str(client) + "--------->")
        print (bcolors.OKBLUE + str(spd.security_policy_database[client]) + bcolors.ENDC)
    print("----END-SPD-------")

def print_sad(sad):
    print("--------SAD------------")
    print(bcolors.HEADER +
    "node-id(target) | subgraph (path/chain) | key (crypto)" +
    bcolors.ENDC)
    for id, sa in sad._security_associations.items():
        print(bcolors.OKGREEN +
        str(id) + " : " + str(sa) +
        bcolors.ENDC)
    print("-------END-SAD------------")

#### --------------------- TESTING ----------------------------
if TESTBED:
    print(channel_graph)
    print("---------TEST-BED----------------")
    #create three groups
    # U = { 0, 1, 2, 3, 4, 5, 6 }
    # g1 = { 1, 3, 4 }
    # g2 = { 2, 5, 6 }
    # g5 = { 5 }
    # g0 = { U }
    n0 = channel_graph.get_node(0)
    n1 = channel_graph.get_node(1)
    n2 = channel_graph.get_node(2)
    n5 = channel_graph.get_node(5)
    groups = []
    groups = {}
    groups[n0.get_id()] = spd.create_group(n0, channel_graph)
    groups[n1.get_id()] = spd.create_group(n1, channel_graph)
    groups[n2.get_id()] = spd.create_group(n2, channel_graph)
    groups[n5.get_id()] = spd.create_group(n5, channel_graph)

    #groups.append(spd.create_group(n0, channel_graph))
    #groups.append(spd.create_group(n1, channel_graph))
    #groups.append(spd.create_group(n2, channel_graph))
    #groups.append(spd.create_group(n5, channel_graph))

    print("---GROUPS----")
    print(type(groups))
    for key, g in groups.items():
        print(key)
        print(g)
    print("--END-GROUPS----")

    #assign groups to clients such that
    # c0 = g0
    # c1 = g1
    # c2 = g2
    # c3 = g5
    spd.add_security_policy(0, groups[0])
    spd.add_security_policy(1, groups[1])
    spd.add_security_policy(2, groups[2])
    spd.add_security_policy(3, groups[5])


    def choose_t(topics=6):
        return randrange(0, topics)

    def choose_c(clients=4):
        return randrange(0, client)

    print_spd(spd)

    sa = sad.client_lookup(0, 4)
    sa = sad.client_lookup(1, 3)
    sa = sad.client_lookup(2, 2)
    sa = sad.client_lookup(3, 6)
    sa = sad.client_lookup(3, 5)
    sa = sad.client_lookup(0, 2)

    print("----collusion----")
    #print_spd(spd)
    #print("\n")
    #for i in range(10):
    #    c = randrange(0,4)
    #    t = randrange(0,6)
    #    print(bcolors.HEADER + "Client="+str(c)+" target="+str(t) + bcolors.ENDC)
    #    sa = sad.client_lookup(c,t)
    #    if not sa:
    #        print(bcolors.FAIL + "FAILED TO FIND SA" + bcolors.ENDC)
    #    else:
    #        print(bcolors.OKGREEN + "GOT SA: "  + str(sa) + bcolors.ENDC)

    #    print_sad(sad)

    #    print("\n")
    #cycle clients topics
    clients = 4
    topics = 7
    sa = None
    for c in range(clients):
        for t in range(topics):
            print(bcolors.HEADER + "Client="+str(c)+" target="+str(t) + bcolors.ENDC)

            #find keys for target
            sec_sa = sad.key_lookup(t)
            t_sa = sad.key_lookup(t)
            #Try to find a SA for target
            if not t_sa:
                print(bcolors.FAIL +
                      "Could not FIND a key for target topic, creating one" +
                      bcolors.ENDC)
            else:
                print(bcolors.OKGREEN +
                      "FOUND TOPIC SA List: " + str(t_sa) +
                      bcolors.ENDC)

            #Try to find a topic/client sa
            sec_sa = sad.find_valid_sa(c, t)


            #Try to create a SA
            if not sec_sa:
                print(bcolors.WARNING +
                      "WARN: NO SA FOR CLIENT AND TOPIC, Creating one" +
                      bcolors.ENDC)
                sec_sa = sad.create_sa_2(c, t)

            if not sec_sa:
                print(bcolors.FAIL +
                      "ERROR: Could not CREATE a sa for client and target" +
                      bcolors.ENDC)

            if sec_sa:
                print(bcolors.OKGREEN +
                      "AUTH SUCCESS: Got Security Association: " + str(sec_sa) +
                      bcolors.ENDC)
            else:
                print(bcolors.FAIL +
                      "AUTH FAILED: for Client: " + str(c) + " on topic: " + str(t) +
                      bcolors.ENDC)
            #print sad and spd
            print_spd(spd)
            print_sad(sad)
            sec_sa = None
            t_sa = None

            print("\n")
    print("----------END COLLUSION------------")


    print("--------END-TEST-BED----------------")

else:
    client_groups = spd.create_group_r(n_groups, channel_graph)
    MAX_V = max(channel_graph._vertices)

    groups_cycle = cycle(client_groups)

    # Round robin group policy assignment
    for client in range(n_clients):
        print("adding spd for c: " + str(client))
        spd.add_security_policy(client, groups_cycle.__next__())


if not INTERACTIVE and not TEST and not TESTBED:
    print("---------NON-INTERACTIVE----------------")

    SP = spd.get_security_policy(client_id)
    SA = None
    keys = channel_graph._vertices.keys()
    for target in keys:
        print("Trying SAD Lookup with target: " + str(target))
        SA = sad.client_lookup(client_id, target)
        if SA:
            break
    print("----")
    if not SA:
        print("NO SA FOUND")
    else:
        print(SA)
        print(SA.sub_graph)
        print(SA.key)
        print_sad(sad)
    print("---------END-NON-INTERACTIVE----------------")

if TEST:
    print("---------TEST----------------")
    print(spd.get_security_policy(client_id).keys())
    sp_keys = list(spd.get_security_policy(client_id).keys())
    print(sp_keys)
    k = choice(sp_keys)
    sec_a = sad.client_lookup(client_id, k)
    print(sec_a.key)
    print(sec_a.sub_graph)
    print("----------END-TEST----------------")

#if TESTBED:





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
