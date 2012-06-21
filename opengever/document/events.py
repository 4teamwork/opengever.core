
from five import grok
from zope.component.interfaces import ObjectEvent

from opengever.document import interfaces


class ObjectCheckedOutEvent(ObjectEvent):
    """ The ObjectCheckedOutEvent is triggered when a object
    was checked out.
    """
    grok.implements(interfaces.IObjectCheckedOutEvent)

    def __init__(self, obj, comment):
        self.object = obj
        self.comment = comment


class ObjectCheckedInEvent(ObjectEvent):
    """ The ObjectCheckedInEvent is triggered when a object
    was checked in.
    """
    grok.implements(interfaces.IObjectCheckedInEvent)

    def __init__(self, obj, comment):
        self.object = obj
        self.comment = comment


class ObjectCheckoutCanceledEvent(ObjectEvent):
    """ The ObjectCheckoutCanceledEvent is triggered when the editing
    of a checked out object is canceled and the working copy is destroyed
    """
    grok.implements(interfaces.IObjectCheckoutCanceledEvent)

    def __init__(self, obj):
        self.object = obj


class ObjectRevertedToVersion(ObjectEvent):
    """The document was reverted back to a specific version.
    """
    grok.implements(interfaces.IObjectRevertedToVersion)

    def __init__(self, obj, version_id, create_version):
        self.object = obj
        self.version_id = version_id
        self.create_version = create_version
