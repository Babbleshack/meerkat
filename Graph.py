class vertix:
    def __init__(self, id, parents, children):
        self._id = id;
        self._parents = parents
        self._children = children

    def get_id(self):
        return self._id

    def get_children(self):
        return self._children

    def get_parents(self):
        return self._parents

class Graph:
    def __init__(self, height, children):
        '''init graph,
        height (int), the number of levels.
        children (int), number of child nodes per node.
        '''
        self._total_v = (children**height) - 1
        self._vertices = {}
        self.init_graph(self._total_v)

    #def create__vertices(self, total):
    #    '''
    #    Create _vertices
    #    '''
    #    for i in range(total):
    #        self._vertices[i] = []
    #    #for i in range(total):
    #    #    self._vertices.append(vertix(i))



    def init_graph(self, total):
        '''
        When o(n) is good enough
        '''
        #change total to len(self._vertices)
        #self._vertices = {range(self._total_v)}
        for i in range(total):
            if i == 0:
                self._vertices[i] = [1, 2]
            else:
                child_ind = (i * 2) + 1
                #find parent
                parent_ind = 0
#                if i in [1, 2]:
#                    parent_ind = 0
#                else:
#
                if child_ind > (total - 1):
                    continue #were done
                #TODO: replace with list comprehension and add
                #children, maybe refactor to func.
                children = [child_ind, child_ind + 1]
                self._vertices[i] = children

    def get_total(self):
        return self._total_v

    def get_children(self, id):
        if id not in self._vertices:
            return False
        return self._vertices[id]


    #def init_edges(self, total):
    #    '''
    #    When o(n) is good enough
    #    '''
    #    #change total to len(self.vertices)
    #    self._edges = {}
    #    for i in range(total):
    #        if i == 0:
    #            self._edges[i] = [1, 2]
    #        else:
    #            child_ind = (i * 2) + 1
    #            if child_ind > (total - 1):
    #                continue #were done
    #            #replace with list comprehension
    #            children = [child_ind, child_ind + 1]
    #            self._edges[i] = children

#g = Graph(4,2) ## limited to two children
#print("---EDGES---")
#for n in g._vertices:
#    for i in g._vertices[n]:
#        print(str(n) + "->" + str(i))
