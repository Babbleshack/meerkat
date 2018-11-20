class vertix:
    def __init__(self, id, parent, children):
        self._id = id;
        self._parent = parent
        self._children = children

    def __str__(self):
        out_str = "id=" + str(self._id)
        out_str += " parent_id="
        if self._parent is None:
            out_str += "None"
        else:
            out_str += str(self._parent.get_id())
        out_str += " children="
        c_ids = []
        for child in self._children:
            c_ids.append(child.get_id())
        out_str += str(c_ids)
        return out_str

    def __repr__(self):
        return self.__str__()


    def get_id(self):
        return self._id

    def get_children(self):
        return self._children

    def set_children(self, children=[]):
        if children is not None:
            self._children = children

    def get_parent(self):
        return self._parent

    def set_parent(self, parent):
        self._parent = parent


class Graph:
    def __init__(self, height, children):
        '''init graph,
        height (int), the number of levels.
        children (int), number of child nodes per node.
        '''
        self._total_v = (children**height) - 1
        self._vertices = {}
        self._number_of_children = children
        self.init_graph(self._total_v)

    def _calc_child_ids (self, id, number_of_children=2):
        '''
        proof this
        '''
        f_child = id * number_of_children
        return [n+1 for n in range(f_child, f_child+number_of_children)]

    def init_graph(self, total):
        '''
        When o(n) is good enough
        Create vertices and child pointers
        '''
        self._vertices = {n: vertix(n, None, []) for n in range(self._total_v)}
        ##itterate vertices and associate with children/parent nodes
        for id, node in self._vertices.items():
            if id == 0:
                self._vertices[id]._parent = None
                if self._total_v > 3:
                    self._vertices[id].set_children([self._vertices[1], self._vertices[2]])
                    self._vertices[1].set_parent(self._vertices[0])
                    self._vertices[2].set_parent(self._vertices[0])
            else:
                child_ind = self._calc_child_ids(id, self._number_of_children)
                if child_ind[0] > (total - 1):
                    continue #break were done
                else:
                    children = [self._vertices[n] for n in child_ind if n < self._total_v]
                    self._vertices[id].set_children(children)
                    for child in children:
                        child.set_parent(self._vertices[id])

    def get_total(self):
        return self._total_v

    def get_node(self, id):
        if id not in self._vertices:
            return None
        return self._vertices[id]

    def get_children(self, id):
        if id not in self._vertices:
            return False
        return self._vertices[id].get_children()

    def traverse(self, node, visited):
        if not visited:
            visited = {}
        visited[node.get_id()] = node
        children = node.get_children()
        for child in node.get_children():
            if type(child) is int:
                    print("Got child of type int: " + str(child))
            if child.get_id() not in visited:
                visited = self.traverse(child, visited)
        return visited

    def path_to_root(self, node, visited=[]):
        visited.append(node.get_id())
        if not node.get_parent():
            return visited
        else:
            return self.path_to_root(node.get_parent(), visited)


    def path(self, src, target, path=None, node=None):
        if path is None:
            path = []
        if node is None:
            node = self.get_node(target)
        c_node = node
        p_node = node.get_parent()
        #add current node to path
        path.append(c_node.get_id())
        if c_node.get_id() < src: # we have traversed a level past the src
            return None
        if c_node.get_id() == src: # we found the src!
            return path[::-1]
        return self.path(src, target, path, p_node) #next node

    def vertices(self):
        return list(self._vertices.keys())

    def vertices_nodes(self):
        return self._vertices

    def print_graph(self):
        for id, node in self._vertices.items():
            for child in node.get_children():
                print(str(node.get_id()) + "->" + str(child.get_id()))

    def __str__(self):
        out_str = ""
        for id, node in self._vertices.items():
            for child in node.get_children():
                out_str += "{} -> {}".format(str(node.get_id()), str(child.get_id()))
                out_str += "\n"
        return out_str;

    def __repr__(self):
        return self.__str__()

#g = Graph(4,2) ## limited to two children
#print(g)
#print(g._vertices[0])
#print("---")
#for id, node in g._vertices.items():
#    print(node)
#
#print(g.traverse(g.get_node(5)))
#
#g.print_graph()

#for id, node in g._vertices.items():
#    for child in node.get_children():
#        print(str(node.get_id()) + "->" + str(child.get_id()))

#print(g.get_node(5))
#print(g.get_node(5).get_children())
#
#print(str(g._vertices))
