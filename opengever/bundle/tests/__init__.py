from collections import OrderedDict
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.interface import implementer


@implementer(IAttributeAnnotatable)
class MockTransmogrifier(object):
    pass


class MockBundle(object):
    def __init__(self):
        self.item_by_guid = OrderedDict()
        self.path_by_refnum_cache = {}
        self.existing_guids = ()
        self.stats = {}
