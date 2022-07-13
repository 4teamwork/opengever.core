from opengever.document import interfaces
from zope.component.interfaces import ObjectEvent
from zope.interface import implementer


@implementer(interfaces.IObjectCheckedOutEvent)
class ObjectCheckedOutEvent(ObjectEvent):
    """The ObjectCheckedOutEvent is triggered when a object
    was checked out.
    """

    def __init__(self, obj, comment):
        self.object = obj
        self.comment = comment


@implementer(interfaces.IObjectBeforeCheckInEvent)
class ObjectBeforeCheckInEvent(ObjectEvent):
    """The ObjectBeforeCheckInEvent is triggered before a object gets
    checked in.
    """

    def __init__(self, obj):
        self.object = obj


@implementer(interfaces.IObjectCheckedInEvent)
class ObjectCheckedInEvent(ObjectEvent):
    """The ObjectCheckedInEvent is triggered when a object
    was checked in.
    """

    def __init__(self, obj, comment):
        self.object = obj
        self.comment = comment


@implementer(interfaces.IObjectCheckoutCanceledEvent)
class ObjectCheckoutCanceledEvent(ObjectEvent):
    """The ObjectCheckoutCanceledEvent is triggered when the editing
    of a checked out object is canceled and the working copy is destroyed.
    """

    def __init__(self, obj):
        self.object = obj


@implementer(interfaces.IObjectRevertedToVersion)
class ObjectRevertedToVersion(ObjectEvent):
    """The document was reverted back to a specific version."""

    def __init__(self, obj, version_id, create_version, comment):
        self.object = obj
        self.version_id = version_id
        self.create_version = create_version
        self.comment = comment


@implementer(interfaces.IFileCopyDownloadedEvent)
class FileCopyDownloadedEvent(ObjectEvent):
    """The file of a document was downloaded."""

    def __init__(self, obj, version_id=None):
        self.object = obj
        self.version_id = version_id


@implementer(interfaces.IFileAttachedToEmailEvent)
class FileAttachedToEmailEvent(ObjectEvent):
    """The file was attached to an email by OfficeConnector."""
