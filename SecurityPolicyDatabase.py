from random import choice, shuffle
from Graph import *

class SecurityPolicyDatabase:
    '''
    client-id | sub-graph
    '''
    def __init__(self):
        self.security_policy_database = {}

    def add_security_policy(self, client_id, sub_graph):
        self.security_policy_database[client_id] = sub_graph

    def get_security_policy(self, client_id):
        return self.security_policy_database[client_id]

    def create_groups(self, number, channel_graph, all_topics=False):
        '''
        returns 'number' random sub-graphs
        plus /* if set to true
        '''
        groups = {}
        vertices = channel_graph.get_vertices()
        for i in number:
            shuffle(vertices)
            s_node = choice(vertices)
            #could choose same twice, remove choice
            groups[s_node] = channel_graph.traverse(s_node)
            del vertices[s_node]
        if all_topics:
            groups[0] = channel_graph
        return groups

    def assign_group(self, client_id, groups):
        group = choice(groups)
        self.security_policy_database[client_id] = group
        return group
