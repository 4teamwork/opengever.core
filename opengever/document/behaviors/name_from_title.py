from opengever.base.interfaces import ISequenceNumber
from plone.app.content.interfaces import INameFromTitle
from zope.component import getUtility
from zope.interface import implements


class IDocumentNameFromTitle(INameFromTitle):
    """Behavior interface.
    """


class DocumentNameFromTitle(object):
    """Speical name from title behavior for letting the normalizing name
    chooser choose the ID like want it to be.
    The of a document should be in the format: "document-{sequence number}"
    """

    implements(IDocumentNameFromTitle)

    format = u'document-%i'

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        seq_number = getUtility(ISequenceNumber).get_number(self.context)
        return self.format % seq_number
