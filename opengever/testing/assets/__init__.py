from os.path import abspath
from os.path import dirname
from os.path import join


def load(asset_filename):
    filepath = join(dirname(abspath(__file__)), asset_filename)
    with open(filepath, 'rb') as asset_file:
        return asset_file.read()
