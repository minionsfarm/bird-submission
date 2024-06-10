import getpass


def flatten(xss):
    return [x for xs in xss for x in xs]


def get_username():
    return getpass.getuser()
