from opengever.api.workspace import delete_workspace_content
from opengever.workspace.utils import is_within_workspace_root
from plone import api
from plone.restapi.services.content.delete import ContentDelete
from zExceptions import Forbidden


class DeleteDocument(ContentDelete):
    """Deletes a document content

    We want to use the default rest-api delete implementation with the default
    permission for gever documents but a special implementation for workspace
    documents.
    """
    def reply(self):
        if is_within_workspace_root(self.context):
            return self.handle_teamraum()
        else:
            return self.handle_gever()

    def handle_teamraum(self):
        if not api.user.has_permission(
                'opengever.workspace: Delete Documents', obj=self.context):
            raise Forbidden()

        delete_workspace_content(self.context)
        return self.reply_no_content()

    def handle_gever(self):
        if not api.user.has_permission('Delete objects', obj=self.context):
            raise Forbidden

        return super(DeleteDocument, self).reply()
