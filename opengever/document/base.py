from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.task.task import ITask
from plone.dexterity.content import Item


class BaseDocument(Item):

    def get_parent_dossier(self):
        """Return the document's parent dossier.

        A parent dossier is available for documents in a dossier/subdossier
        or for documents in a task.

        No parent dossier is available for documents in an inbox, in a
        forwarding or inside a proposal. In that case this method returns None.

        """
        parent = aq_parent(aq_inner(self))
        if IDossierMarker.providedBy(parent):
            return parent
        if ITask.providedBy(parent):
            return parent.get_containing_dossier()

        return None
