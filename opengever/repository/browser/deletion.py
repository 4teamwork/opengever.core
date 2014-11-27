from AccessControl import Unauthorized
from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from opengever.repository import _
from opengever.repository.deleter import RepositoryDeleter
from opengever.repository.repositoryfolder import IRepositoryFolderSchema
from Products.statusmessages.interfaces import IStatusMessage
from zope.interface import Interface


class RepositoryDeletionView(grok.View):
    """Repository deletion view, including a delete confirmation.
    """
    grok.context(IRepositoryFolderSchema)
    grok.name('delete_repository')
    grok.require('zope2.DeleteObjects')
    grok.template('deletion')

    def __call__(self):
        self.parent = aq_parent(aq_inner(self.context))

        deleter = RepositoryDeleter(self.context)

        if not deleter.is_deletion_allowed():
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


class RepositoryDeletionAllowed(grok.View):
    grok.context(Interface)
    grok.name('is_deletion_allowed')
    grok.require('zope2.View')

    def render(self):
        if IRepositoryFolderSchema.providedBy(self.context):
            deleter = RepositoryDeleter(self.context)
            return deleter.is_deletion_allowed()

        return False
