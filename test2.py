class vertix:
    def __init__(self, id):
        self.id = id;

class Graph:
    def __init__(self, height, children):
        total_v = (height * children) + 1
        self.vertices = []
        self.edges = {}
        self.create_vertices(total_v)
        self.init_edges(total_v)

    def create_vertices(self, total):
        for i in range(total):
            self.vertices[i] = vertix(i);

    def init_edges(self, total):
        self._edges = {}
        for i in range(total):
            if i == 0:
                self._edges = {i, [1,2]}
            else:
                child_ind = (i * 2) + 1
                if child_ind > total:
                    break #were done
                self._edges[i].append(child_ind)
                self._edges[i].append(child_ind + 1)
