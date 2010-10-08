from opengever.base.interfaces import ISequenceNumber
from plone.app.content.interfaces import INameFromTitle
from zope.component import getUtility
from zope.interface import implements


class IDossierNameFromTitle(INameFromTitle):
    """Behavior interface.
    """


class DossierNameFromTitle(object):
    """Speical name from title behavior for letting the normalizing name
    chooser choose the ID like want it to be.
    The of a dossier should be in the format: "dossier-{sequence number}"
    """

    implements(IDossierNameFromTitle)

    format = u'dossier-%i'

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        seq_number = getUtility(ISequenceNumber).get_number(self.context)
        return self.format % seq_number
