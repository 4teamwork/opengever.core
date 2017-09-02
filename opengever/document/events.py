from five import grok
from opengever.document import interfaces
from zope.component.interfaces import ObjectEvent
from zope.interface import implements


class ObjectCheckedOutEvent(ObjectEvent):
    """The ObjectCheckedOutEvent is triggered when a object
    was checked out.
    """

    grok.implements(interfaces.IObjectCheckedOutEvent)

    def __init__(self, obj, comment):
        self.object = obj
        self.comment = comment


class ObjectBeforeCheckInEvent(ObjectEvent):
    """The ObjectBeforeCheckInEvent is triggered before a object gets
    checked in.
    """

    grok.implements(interfaces.IObjectBeforeCheckInEvent)

    def __init__(self, obj):
        self.object = obj


class ObjectCheckedInEvent(ObjectEvent):
    """The ObjectCheckedInEvent is triggered when a object
    was checked in.
    """

    grok.implements(interfaces.IObjectCheckedInEvent)

    def __init__(self, obj, comment):
        self.object = obj
        self.comment = comment


class ObjectCheckoutCanceledEvent(ObjectEvent):
    """The ObjectCheckoutCanceledEvent is triggered when the editing
    of a checked out object is canceled and the working copy is destroyed.
    """

    grok.implements(interfaces.IObjectCheckoutCanceledEvent)

    def __init__(self, obj):
        self.object = obj


class ObjectRevertedToVersion(ObjectEvent):
    """The document was reverted back to a specific version."""

    grok.implements(interfaces.IObjectRevertedToVersion)

    def __init__(self, obj, version_id, create_version):
        self.object = obj
        self.version_id = version_id
        self.create_version = create_version


class FileCopyDownloadedEvent(ObjectEvent):
    """The file of a document was downloaded."""

    grok.implements(interfaces.IFileCopyDownloadedEvent)

    def __init__(self, obj, version_id=None):
        self.object = obj
        self.version_id = version_id


class FileAttachedToEmailEvent(ObjectEvent):
    """The file was attached to an email by OfficeConnector."""

    implements(interfaces.IFileAttachedToEmailEvent)
