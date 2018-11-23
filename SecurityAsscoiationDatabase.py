import uuid

from Graph import *
import SecurityPolicyDatabase

class SecurityAssociation:
    def __init__(self, sa_id, sub_graph, key):
        self.sub_graph = sub_graph
        self.key = key
        self.id = sa_id
        if type(sub_graph) == 'int':
            print("GOT BULLSHIT SA")
            print(self)


    def __str__(self):
        out_str = '[ '
        out_str += 'key = '
        out_str += str(self.key)
        out_str += ', '
        out_str += "s_graph: "
        out_str += str(self.sub_graph)
        out_str += "]"
        return out_str

    def __repr__(self):
        return self.__str__()

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
    def key_lookup(self, target):
        '''
        return every key 'target appears in
        '''
        sa_list = []
        for id, sa in self._security_associations.items():
            keys = sa.sub_graph
            #print("+++++++++")
            #print(keys)
            #print(sa)
            #print("+++++++++")
            if target in keys:
                sa_list.append(sa)
        return sa_list

    def find_valid_sa(self, client_id, target):
        '''
        Find a valid sa for a given target node for a client
        '''
        sp = self._security_policies.get_security_policy(client_id)
        #find all valid sa for topic
        if sp is None:
            return None
        sp_set = set(sp.keys())
        #for id, sa in self._security_associations:
        #    sg_set = set(sa.sub_graph)
        #    if sg_set.issubset(sp_set):
        #        return sa
        #refactored: faster to get all sa for a topic, and then
        # check each for valid sa.
        topic_sa_list = self.key_lookup(target)
        if not topic_sa_list:
            return None
        for t_sa in topic_sa_list:
            t_set = set(t_sa.sub_graph)
            if t_set.issubset(sp_set): #is the sa a subset of policy?
                return t_sa
        return None


    def create_sa_2(self, client_id, target, key=None):
        '''
        Creates a new SA
        finds path between SP root and Target
        Creates new policy
        '''
        if not key:
            key = self.generate_key()
        #get sec policies
        sp = self._security_policies.get_security_policy(client_id)
        if sp is None:
            return None
        #find root of sp
        sp_r = min(sp.keys())
        #path between sp-root and target
        path = self._channel_graph.path(sp_r, target)
        if not path:
            return None
        #ensure association is valid
        sa_set = set(path)
        sp_set = set(sp.keys())
        if not sa_set.issubset(sp_set): #Cannot create valid SP set
            return None
        #add new sa to database
        sa = SecurityAssociation(target, path, key)
        self._security_associations[target] = sa
        return sa

    def create_sa(self, sp, target):
        '''
        creates a new sa with subgraph traversal from
        sa_key.
        '''
        g_root = min(sp)
        path = self._channel_graph.path(g_root, target)
        key = self.generate_key()
        return SecurityAssociation(target, path, key)




    #We receive a message from client 'Cx'
    # Tries to authorised client on channel.
    # If one cannot be found creates one
    def client_lookup(self, client_id, target):
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
        print("Found SP: " + str(sp))
        #check if target is in sp
        sp_keys = set(sp.keys())
        print("Got sp key set")
        print(sp_keys)
        #print(target)
        #print(str(sp_keys))
        if target not in sp_keys:
            print("target not in sp_keys")
            return False
        #Find SA subgraph of clients SP.
        security_association = None
        for id, sa in self._security_associations.items():
            print (sa.sub_graph)
            #sa_keys = set(sa.sub_graph.keys())
            sa_keys = set(sa.sub_graph)
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



