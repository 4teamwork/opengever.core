from zope.component.interfaces import IObjectEvent
from zope.component.interfaces import ObjectEvent
from zope.interface import implements


class IRepositoryPrefixUnlocked(IObjectEvent):
    """ A repository prefix has been unlocked. """


class RepositoryPrefixUnlocked(ObjectEvent):
    implements(IRepositoryPrefixUnlocked)

    def __init__(self, object, prefix):
        ObjectEvent.__init__(self, object)
        self.prefix = prefix
