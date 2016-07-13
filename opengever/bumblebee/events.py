from five import grok
from opengever.bumblebee.interfaces import IPDFDownloadedEvent
from zope.component.interfaces import ObjectEvent


class PDFDownloadedEvent(ObjectEvent):
    """The PDFDownloaded Event is triggered when the converted PDF for an
    object is downloaded from bumblebee.
    """

    grok.implements(IPDFDownloadedEvent)
