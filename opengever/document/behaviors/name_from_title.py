from opengever.base.interfaces import ISequenceNumber
from plone.app.content.interfaces import INameFromTitle
from zope.component import getUtility
from zope.interface import implements


class IDocumentNameFromTitle(INameFromTitle):
    """Behavior interface.
    """


class DocumentNameFromTitle(object):
    """Customized name from title behavior for using the normalizing name
    chooser to select a document ID according to our specifications.
    The ID of a document will be in the format: "document-{sequence number}"
    """

    implements(IDocumentNameFromTitle)

    format = u'document-%i'

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        seq_number = getUtility(ISequenceNumber).get_number(self.context)
        return self.format % seq_number
