from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.listing_actions import BaseListingActions
from opengever.private.dossier import IPrivateDossier
from opengever.trash.trash import ITrasher
from plone import api
from plone.dexterity.interfaces import IDexterityContainer
from zope.component import adapter


@adapter(IDexterityContainer, IOpengeverBaseLayer)
class TrashListingActions(BaseListingActions):

    def is_remove_available(self):
        return api.user.has_permission('Remove GEVER content', obj=self.context)

    def is_untrash_content_available(self):
        if not api.user.has_permission('opengever.trash: Untrash content', obj=self.context):
            return False
        return not ITrasher(self.context).is_trashed()


@adapter(IPrivateDossier, IOpengeverBaseLayer)
class PrivateDossierTrashListingActions(TrashListingActions):

    def is_remove_available(self):
        return False


class WorkspaceTrashListingActions(TrashListingActions):

    def is_delete_workspace_content_available(self):
        return (api.user.has_permission('opengever.workspace: Delete Documents', obj=self.context)
                and api.user.has_permission('opengever.workspace: Delete Workspace Folders',
                                            obj=self.context))

    def is_remove_available(self):
        return False

    def is_delete_available(self):
        return False
