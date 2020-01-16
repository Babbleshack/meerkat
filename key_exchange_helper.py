#! /usr/bin/env python3
import json
from logger import *


def replace_topic_str(topic_str, new_target, seperator="/"):
    topics = topic_str.split(seperator)
    topics[-1] = new_target
    return seperator.join(topics)

def validate_msg(msg):
    valid = True
    if not 'source_id' in msg:
        print_warning("WARNING:: validate_msg::Cannot find client id")
        valid = False
    if not 'target' in msg:
        print_warning("WARNING:: validate_msg::Cannot find target")
        valid = False
    if not 'payload' in msg:
        print_warning("WARNING:: validate_msg::Cannot find message payload")
        valid = False
    return valid

def create_msg_packet(source_id, target, payload, json_encode=False):
    '''
    target should be PUBLISH | KEY-REQUEST | RESPONSE
    '''
    packet = {
        'source_id': source_id,
        'target' : target,
        'payload' : payload
    }
    return json.dumps(packet) if json_encode else packet

def parse_request_packet(request_packet):
    r_packet = None
    try:
        r_packet = json.loads(request_packet)
    except:
        print_fail("ERROR: Failed to parse request packet:\n{}".format(request_packet))
        return r_packet


def validate_request_packet(request_packet):
    valid = True
    if not 'target' in request_packet:
        valid = False
    if not 'client_id' in request_packet:
        valid = False
    return valid

def create_request_packet(target, client_id, json_encode=False):
    packet = {
        'target' : target,
        'client_id' : client_id
    }
    return json.dumps(packet) if json_encode else packet

def create_response_packet(client, target, sa, json_encode=False):
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

def validate_response_packet(response_packet):
    valid = True
    if not 'client_id' in response_packet:
        valid = False
        print_warning("WARNING:: validate_response_packet: cannot find client id")
    if not 'target' in response_packet:
        valid = False
        print_warning("WARNING:: validate_response_packet: cannot find target")
    if not 'path' in response_packet:
        valid = False
        print_warning("WARNING:: validate_response_packet: cannot find path")
    if not 'key' in response_packet:
        valid = False
        print_warning("WARNING:: validate_response_packet: cannot find key")
    return valid

def wrap_packet(source_id, target, data, json_encode=False):
    '''
    DEPRECATED
    target should be PUBLISH | KEY-REQUEST | RESPONSE
    '''
    packet = {
        'source_id' : source_id,
        'target' : target,
        'payload': data
    }
    return json.dumps(packet) if json_encode else packet

def create_enc_message(topic_id, key, payload, json_encode=False):
    packet = {
        'payload': payload,
        'key': key,
        'topic_id': topic_id
    }
    return json.dumps(packet) if json_encode else packet

def validate_enc_message(packet):
    valid = True
    if not 'payload' in packet:
        valid = False
    if not 'key' in packet:
        valid = False
    if not 'topic_id' in packet:
        valid = False
    return valid

def print_spd(spd, title='SPD'):
    print("-----------{}-------------".format(title))
    print("client-id | subgraph")
    for id, policy in spd.security_policy_database.items():
        print("[{}] :: [{}]".format(str(id), str(policy)))
    print("----END-SPD-------")

def print_sad(sad, title='SAD'):
    print("--------{}------------".format(title))
    print("node-id(target) | subgraph (path/chain) | key (crypto)")
    for id, sa in sad._security_associations.items():
        print("{} :: {}".format(str(id), str(sa)))
    print("-------END-SAD------------")
