from opengever.base.context_actions import BaseContextActions
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.listing_actions import BaseListingActions
from opengever.workspace.interfaces import IToDo
from plone import api
from plone.dexterity.interfaces import IDexterityContainer
from zope.component import adapter


@adapter(IDexterityContainer, IOpengeverBaseLayer)
class WorkspaceFolderListingActions(BaseListingActions):

    def is_copy_items_available(self):
        return True

    def is_move_items_available(self):
        return True

    def is_trash_content_available(self):
        return api.user.has_permission('opengever.trash: Trash content', obj=self.context)


@adapter(IToDo, IOpengeverBaseLayer)
class TodoContextActions(BaseContextActions):

    def is_share_content_available(self):
        return True

    def is_edit_available(self):
        return api.user.has_permission('Modify portal content', obj=self.context)
