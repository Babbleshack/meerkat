from random import choice, shuffle
from Graph import *

class SecurityPolicyDatabase:
    def __init__(self):
        '''
        security policy database describes client-id | sub-graph mapping
        '''
        self.security_policy_database = {}
        self.policies = []

    def add_policy(self, group):
        self.policies.append(group)

    def add_security_policy(self, client_id, sub_graph):
        self.security_policy_database[client_id] = sub_graph

    def get_security_policy(self, client_id):
        if client_id not in self.security_policy_database:
            return None
        return self.security_policy_database[client_id]

    def get_database(self):
        return self.security_policy_database;

    def create_groups(self, number, channel_graph, all_topics=False):
        '''
        returns 'number' random sub-graphs
        plus /* if set to true
        '''
        groups = {}
        vertices = channel_graph.vertices()
        for i in range(number):
            shuffle(vertices)
            s_node = choice(vertices)
            #could choose same twice, remove choice
            groups[i] = channel_graph.traverse(channel_graph.get_node(s_node))
            n_ind = vertices.index(s_node)
            del vertices[n_ind]
        if all_topics:
            groups[0] = channel_graph
        return groups


    def create_group_r(self, number, channel_graph):
        '''
        Create `number` random groups.
        Universal groups will not be created
        see create_group
        '''
        v_list = channel_graph.vertices()
        if number > (len(v_list) - 1):
            print("Error: More groups than vertices chosen")
            raise LookupError("More groups than available vertices requested")
        groups = []
        del v_list[0]
        for i in range(number):
            s_node = choice(v_list)
            del v_list[v_list.index(s_node)]
            node = channel_graph.get_node(s_node)
            group = self.create_group(node, channel_graph)
            groups.append(group)
        return groups

    def create_group(self, node, channel_graph):
        '''
        Create group by traversing from node, to end of graph
        '''
        group = channel_graph.traverse(node, {})
        return group

    def assign_group(self, client_id, group):
        self.security_policy_database[client_id] = group
        return group
