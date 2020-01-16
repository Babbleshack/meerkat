class c_codes:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def print_header(string):
    print(c_codes.HEADER + string + c_codes.ENDC)

def print_okblue(string):
    print(c_codes.OKBLUE + string + c_codes.ENDC)

def print_okgreen(string):
    print(c_codes.OKGREEN + string + c_codes.ENDC)

def print_warning(string):
    print(c_codes.WARNING + string + c_codes.ENDC)

def print_fail(string):
    print(c_codes.FAIL + string + c_codes.ENDC)

def string_header(string):
    return (c_codes.HEADER + string + c_codes.ENDC)

def string_okblue(string):
    return (c_codes.OKBLUE + string + c_codes.ENDC)

def string_okgreen(string):
    return (c_codes.OKGREEN + string + c_codes.ENDC)

def string_warning(string):
    return (c_codes.WARNING + string + c_codes.ENDC)

def string_fail(string):
    return (c_codes.FAIL + string + c_codes.ENDC)
