from five import grok
from opengever.trash import _
from opengever.trash.remover import RemoveConditions
from opengever.trash.remover import Remover
from Products.statusmessages.interfaces import IStatusMessage
from zope.interface import Interface


class RemoveConfirmation(grok.View):
    """Remove Confirmation View, allways displayed in a overlay.
    """
    grok.context(Interface)
    grok.name('remove_confirmation')
    grok.require('zope2.View')
    grok.template('remove_confirmation')

    def __call__(self):
        if self.request.get('form.buttons.delete'):
            self.delete_objects()
            msg = _(u'label_successfully_deleted',
                    default=u'The documents are succesfully deleted')
            IStatusMessage(self.request).addStatusMessage(msg, type='info')
            return self.redirect_back()

        elif self.request.get('form.cancelled'):
            return self.redirect_back()

        if not self.context.REQUEST.get('paths'):
            msg = _(u'error_no_documents_selected',
                    default=u'You have not selected any items')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return self.redirect_back()

        self.verify_documents()

        return super(RemoveConfirmation, self).__call__()

    def redirect_back(self):
        return self.context.REQUEST.RESPONSE.redirect(
            '{}#trash'.format(self.context.absolute_url()))

    def verify_documents(self):
        self.items = []
        self.allowed = True

        for document in self.get_selected_documents():
            condition = RemoveConditions(document)
            allowed = condition.remove_allowed()
            self.items.append({'document': document,
                               'allowed': allowed,
                               'error_msg': condition.error_msg})
            if not allowed:
                self.allowed = False

    def get_selected_documents(self):
        self.paths = self.context.REQUEST.get('paths')
        documents = []
        for path in self.paths:
            documents.append(self.context.unrestrictedTraverse(path))

        return documents

    def delete_objects(self):
        documents = self.get_selected_documents()
        Remover(documents).remove()
