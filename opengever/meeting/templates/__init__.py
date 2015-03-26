from os.path import abspath
from os.path import dirname
from os.path import join


def path(filename):
    return join(dirname(abspath(__file__)), filename)
