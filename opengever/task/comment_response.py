from opengever.task.interfaces import ICommentResponseHandler
from plone import api
from zope.interface import implements


class CommentResponseHandler(object):
    implements(ICommentResponseHandler)

    def __init__(self, context):
        self.context = context

    def is_allowed(self):
        """Allow if:
        - the user has AddPortalContent permission and
        - the containting dossier is open

        if the task is not within a dossier, it only checks the permission
        """
        containing_dossier = self.context.get_containing_dossier()

        return (containing_dossier.is_open() if containing_dossier else True) and \
            api.user.has_permission('Add portal content', obj=self.context)
