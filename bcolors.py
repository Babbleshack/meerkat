class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

    def print_header(self, string):
        print(self.HEADER + string + self.ENDC)

    def print_okblue(self, string):
        print(self.OKBLUE + string + self.ENDC)

    def print_okgreen(self, string):
        print(self.OKGREEN + string + self.ENDC)

    def print_warning(self, string):
        print(self.WARNING + string + self.ENDC)

    def print_fail(self, string):
        print(self.FAIL + string + self.ENDC)

    def string_header(self, string):
        return (self.HEADER + string + self.ENDC)

    def string_okblue(self, string):
        return (self.OKBLUE + string + self.ENDC)

    def string_okgreen(self, string):
        return (self.OKGREEN + string + self.ENDC)

    def string_warning(self, string):
        return (self.WARNING + string + self.ENDC)

    def string_fail(self, string):
        return (self.FAIL + string + self.ENDC)
