import uuid

from Graph import *
import SecurityPolicyDatabase
from logger import *
from key_exchange_helper import print_spd
from key_exchange_helper import print_sad

class SecurityAssociation:
    def __init__(self, sa_id, sub_graph, key):
        self.sub_graph = sub_graph
        self.key = key
        self.id = sa_id
        if type(sub_graph) == 'int':
            print("GOT BULLSHIT SA")
            print(self)

    def get_id(self):
        return self.id

    def get_sub_graph(self):
        return self.sub_graph

    def get_key(self):
        return self.key


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

    def add_security_association(self, target, sa):
        print_okblue("Adding new SA [{}] for target [{}]".format(sa, target))
        self._security_associations[target] = sa

    def remove_security_association(self, sec_asoc):
        for t_id, sa in self._security_associations.items():
            if sec_asoc.key == sa.key:
                del self._security_associations[t_id]
                return True
        return False

    def generate_key(self):
        return uuid.uuid4().hex
                #new SA

    def key_lookup(self, target):
        '''
        return every key 'target appears in
        target is same type as key of vertices
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
        topic_sa_list = self.key_lookup(target)
        if not topic_sa_list:
            return None
        for t_sa in topic_sa_list:
            t_set = set(t_sa.sub_graph)
            if t_set.issubset(sp_set): #is the sa a subset of policy?
                return t_sa
        return None


    def create_sa(self, client_id, target, key=None):
        '''
        Creates a new SA
        finds path between SP root and Target
        Creates new policy
        '''
        if not key:
            key = self.generate_key()
        #get sec policies
        print("Checking client id for")
        sp = self._security_policies.get_security_policy(client_id)
        if sp is None:
            print("NO SP FOUND!")
            return None
        #find root of sp
        sp_r = min(sp.keys())
        #path between sp-root and target
        if target == 0: #topic tree root
            print("Creating root path")
            path = self._channel_graph.vertices()
            print(path)
        else:
            path = self._channel_graph.path(sp_r, target)
        if not path:
            return None
        #ensure association is valid
        sa_set = set(path)
        sp_set = set(sp.keys())
        if not sa_set.issubset(sp_set): #Cannot create valid SP set
            print("bad sp set")
            return None
        #add new sa to database
        sa = SecurityAssociation(target, path, key)
        self._security_associations[target] = sa
        return sa
