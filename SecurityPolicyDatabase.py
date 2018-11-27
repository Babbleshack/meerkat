from random import choice, shuffle
from Graph import *

class SecurityPolicyDatabase:
    def __init__(self):
        '''
        security policy database describes client-id | sub-graph mapping
        '''
        self.security_policy_database = {}
        self.policies = []

    def add_security_policy(self, client_id, sub_graph):
        self.security_policy_database[client_id] = sub_graph

    def get_security_policy(self, client_id):
        if client_id not in self.security_policy_database:
            return None
        return self.security_policy_database[client_id]

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

