class SPD:
    '''
    Security Policy Database
    '''

    def __init__(self, channel_graph, groups={}):
        self._channel_graph = channel_graph
        self._groups = groups
