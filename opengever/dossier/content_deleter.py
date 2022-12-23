from opengever.base.browser.folder_buttons_availability import FolderButtonsAvailabilityView
from opengever.base.content_deleter import BaseContentDeleter
from opengever.dossier.behaviors.dossier import IDossierMarker
from zExceptions import Forbidden
from zope.component import adapter


@adapter(IDossierMarker)
class DossierDeleter(BaseContentDeleter):

    permission = 'opengever.dossier: Delete dossier'

    def verify_may_delete(self, **kwargs):
        super(DossierDeleter, self).verify_may_delete()

        if not self.context.objectCount() == 0:
            raise Forbidden()

        if FolderButtonsAvailabilityView(self.context, None)._has_linked_workspaces():
            raise Forbidden()
