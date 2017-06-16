from opengever.briefbutler.interfaces import IBriefButler
from zope.interface import implements


class FakeButler(object):

    implements(IBriefButler)

    def send(self, document, data):
        pass

