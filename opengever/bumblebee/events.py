from opengever.bumblebee.interfaces import IPDFDownloadedEvent
from zope.component.interfaces import ObjectEvent
from zope.interface import implements


class PDFDownloadedEvent(ObjectEvent):
    """The PDFDownloaded Event is triggered when the converted PDF for an
    object is downloaded from bumblebee.
    """

    implements(IPDFDownloadedEvent)
