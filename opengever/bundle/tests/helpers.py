from argparse import Namespace


"""Miscellaneous test helpers.
"""


def get_title(item):
    title = item.get('title_de', item.get('title'))
    if not title:
        # fallback for ogds_users
        title = item.get('userid')

    return title


def get_portal_type(item):
    _type = item['_type']
    return _type.split('.')[-1]


class FakeDBTab(object):

    def __init__(self, blob_dir):
        storage = Namespace(blob_dir=blob_dir)
        config = Namespace(storage=storage)
        self._factory = Namespace(config=config)

    def getDatabaseFactory(self, name=None, mount_path=None):
        return self._factory


def make_fake_fileloader_configuration(blob_dir):
    return Namespace(dbtab=FakeDBTab(blob_dir))
