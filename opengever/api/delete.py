from opengever.workspace.interfaces import IDeleter
from opengever.workspace.utils import is_within_workspace_root
from plone import api
from plone.restapi.services.content.delete import ContentDelete
from zExceptions import Forbidden
from zope.component import queryAdapter


class GeverContentDelete(ContentDelete):
    """Deletes an object

    We want to use the default rest-api delete implementation with the default
    permission for gever but a special implementation for workspace objects.
    """
    def reply(self):
        if is_within_workspace_root(self.context):
            return self.handle_teamraum()
        else:
            return self.handle_gever()

    def handle_teamraum(self):
        deleter = queryAdapter(self.context, IDeleter)
        if deleter is None:
            raise Forbidden()
        deleter.delete()
        return self.reply_no_content()

    def handle_gever(self):
        if not api.user.has_permission('Delete objects', obj=self.context):
            raise Forbidden()

        return super(GeverContentDelete, self).reply()
