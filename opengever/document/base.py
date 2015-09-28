from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.browser.helper import get_css_class
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.meeting.proposal import IProposal
from opengever.task.task import ITask
from plone import api


class BaseDocumentMixin(object):
    """Abstract base class for document-ish content types."""

    removed_state = None
    active_state = None

    remove_transition = None
    restore_transition = None

    def css_class(self):
        return get_css_class(self)

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
        if IProposal.providedBy(parent):
            return parent.get_containing_dossier()

        return None

    @property
    def is_removed(self):
        return api.content.get_state(obj=self) == self.removed_state

    def related_items(self):
        raise NotImplementedError

    def checked_out_by(self):
        raise NotImplementedError

    def is_checked_out(self):
        raise NotImplementedError

    def get_current_version(self):
        raise NotImplementedError
