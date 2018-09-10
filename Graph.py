class vertix:
    def __init__(self, id, parent, children):
        self._id = id;
        self._parent = parent
        self._children = children

    def __str__(self):
        out_str = "id=" + str(self._id)
        out_str += " parent_id="
        if self._parent is None:
            out_str += "0"
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
        f_child = id * number_of_children
        return [n+1 for n in range(f_child, f_child+number_of_children)]

    def init_graph(self, total):
        '''
        When o(n) is good enough
        '''
        self._vertices = {n: vertix(n, None, []) for n in range(self._total_v)}
        ##itterate vertices and associate with children/parent nodes
        for id, node in self._vertices.items():
            if id == 0:
                self._vertices[id]._parent = None
                if self._total_v > 3:
                    self._vertices[id].set_children([self._vertices[1], self._vertices[2]])
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
        return self._vertices[id]

    def get_children(self, id):
        if id not in self._vertices:
            return False
        return self._vertices[id]

    def traverse(self, node, visited=[]):
        visited.append(node)
        children = node.get_children()
        for child in node.get_children():
            if child.get_id() not in visited:
                visited = self.traverse(child, visited)
        return visited



g = Graph(4,2) ## limited to two children
print(g._vertices[0])
print("---")
for id, node in g._vertices.items():
    print(node)

print(g.traverse(g.get_node(5)))

for id, node in g._vertices.items():
    for child in node.get_children():
        print(str(node.get_id()) + "->" + str(child.get_id()))

