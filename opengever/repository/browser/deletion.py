from AccessControl import Unauthorized
from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.interfaces import IDeleter
from opengever.repository import _
from opengever.repository.repositoryfolder import IRepositoryFolderSchema
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getAdapter


class RepositoryDeletionView(BrowserView):
    """Repository deletion view, including a delete confirmation.
    """

    def __call__(self):
        self.parent = aq_parent(aq_inner(self.context))

        deleter = getAdapter(self.context, IDeleter)

        if not deleter.is_delete_allowed():
            raise Unauthorized

        if self.request.get('form.buttons.cancel'):
            return self.redirect_back()

        elif self.request.get('form.buttons.delete'):
            # Made form CSRF save
            if not self.request.method.lower() == 'post':
                raise Unauthorized

            deleter.delete()

            msg = _(u'label_successfully_deleted',
                    default=u'The repository have been successfully deleted.')
            IStatusMessage(self.request).addStatusMessage(msg, type='info')
            return self.redirect_to_parent()

        return super(RepositoryDeletionView, self).__call__()

    def redirect_to_parent(self):
        return self.context.REQUEST.RESPONSE.redirect(
            self.parent.absolute_url())

    def redirect_back(self):
        return self.context.REQUEST.RESPONSE.redirect(
            self.context.absolute_url())


class RepositoryDeletionAllowed(BrowserView):

    def __call__(self):
        if IRepositoryFolderSchema.providedBy(self.context):
            deleter = getAdapter(self.context, IDeleter)
            return deleter.is_delete_allowed()

        return False
