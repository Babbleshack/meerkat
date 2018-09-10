import uuid

from Graph import *
import SecurityPolicyDatabase

class SecurityAssociation:
    def __init__(self, sub_graph, key):
        self.sub_graph = sub_graph
        self.key = key

class SecurityAssociationDatabase:
    '''
    channel_id | sub-graph (group) | key
    '''
    def __init__(self, spd, channel_graph):
        self._security_associations = {}
        self._security_policies = spd
        self._channel_graph = channel_graph

    def generate_key(self):
        return uuid.uuid4().hex
                #new SA
    def client_lookup(self, target, client_id):
        '''
        if:
        target not in SPD for client , return false
        else:
        check if target in SAD, check spd.sub_graph, is subset of sad.sub_graph
        else:
        create new key from target to bottom of tree
        '''
        sp = self._security_policies.get_security_policy(client_id)
        sp_keys = set(sp.keys())
        security_association = None
        if target not in sp_keys:
            return False
        for id, sa in self._security_associations.items():
            sa_keys = set(sa.keys())
            if sa_keys.issubset(sp_keys):
                security_association = sa
        if not security_association:
            group = self._channel_graph.traverse(target)
            key = self.generate_key()
            security_association =  SecurityAssociation(g, key)
            self._security_associations[target] = security_association
        return security_association

    def key_lookup(self, channel_id):
        sa = None
        path = sorted(self._channel_graph.path_to_root(channel_id))
        for id in path[::-1]:
            if id in self._security_associations:
                sa = self._security_associations[id]
                sa_id = channel_id
        if not sa:
            group = self._channel_graph.traverse(0)
            sa = SecurityAssociation(graph, self.generate_key)
            self._security_associations[0] = sa
        return sa



