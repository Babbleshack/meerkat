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
    #We receive a message from client 'Cx'
    # Tries to authorised client on channel.
    # If one cannot be found creates one
    def client_lookup(self, target, client_id):
        '''
        Tries to find sa in database
        if no sa is found checks spd for client
        creates subgraph from target to bottom of tree
        TODO: target for refactor
        if:
        target not in SPD for client , return false
        else:
        check if target in SAD, check spd.sub_graph, is subset of sad.sub_graph
        else:
        create new key from target to bottom of tree
        '''
        #check if sp can be found
        sp = self._security_policies.get_security_policy(client_id)
        if sp is None:
            return False
        #check if target is in sp
        sp_keys = set(sp.keys())
        if target not in sp_keys:
            return False
        #Find SA subgraph of clients SP.
        security_association = None
        for id, sa in self._security_associations.items():
            sa_keys = set(sa.keys())
            if sa_keys.issubset(sp_keys):
                security_association = sa
        #No SA found create a new one
        if not security_association:
            security_association = self.create_sa(sp, target)
            self._security_associations[target] = security_association
        return security_association

    #def _create_security_association(self, target):
    #    group = self._channel_graph.traverse(target)
    #    key = self.generate_key()
    #    security_association = SecurityAssociation(group, key)
    #    return security_association

    def create_sa(self, sp, target):
        '''
        creates a new sa with subgraph traversal from
        sa_key.
        '''
        g_root = min(sp)
        path = self._channel_graph.path(g_root, target)
        key = self.generate_key()
        return SecurityAssociation(path, key)

    ##When sending a message on channel 'x'
    ##find all relevent keys.
    #def key_lookup(self, channel_id):
    #    sa = None
    #    path = sorted(self._channel_graph.path_to_root(channel_id))
    #    for id in path[::-1]:
    #        if id in self._security_associations:
    #            sa = self._security_associations[id]
    #            sa_id = channel_id
    #    #TODO: Refactor to method, return null here instead.
    #    #if no valid SA found make
    #    if not sa:
    #        group = self._channel_graph.traverse(0)
    #        sa = SecurityAssociation(group, self.generate_key)
    #        self._security_associations[0] = sa
    #    return sa



