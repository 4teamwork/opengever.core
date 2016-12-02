from collections import OrderedDict


class MockTransmogrifier(object):

    def __init__(self):
        self.item_by_guid = OrderedDict()
