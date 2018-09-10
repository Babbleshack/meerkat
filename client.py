class client:
    """Client class provide mechanisms for managing
    sad.
    """
    def __init__(self, SPD, channels):
        self.sad = {}
        self.spd = SPD
        self._cTree = channels


    '''
    channel-uri|key
    0/1/2/*
    '''

    def lookup_sad(self, channel_uri):
        elements = channel_uri.split("/")
        self
        if channel in self.sad:
            return self.sad[channel]
        return -1

    def add_sad_entry(self, channel, key):


