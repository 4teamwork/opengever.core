from opengever.base.interfaces import ISequenceNumber
from opengever.workspace.interfaces import IWorkspace
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

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        seq_number = getUtility(ISequenceNumber).get_number(self.context)
        return self.format % seq_number

    @property
    def format(self):
        """ Since the workspace content type provides IDossierMarker, we cant
            create a new interface to provide INameFromTitle for workspaces.
            Plone cant decide which one to use if we register another interface
            prividing the same thing, so it decides to use none of them.
            To work around this, we can simply check if the content type is
            a workspace in here to decide which format to use.
        """
        if IWorkspace.providedBy(self.context):
            return u'workspace-%i'
        return u'dossier-%i'
