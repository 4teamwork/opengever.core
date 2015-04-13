from opengever.base.model import create_session
from opengever.meeting import _
from plone import api
from Products.Five.browser import BrowserView
from zExceptions import NotFound
from zExceptions import Unauthorized
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserView


class RemoveModelView(BrowserView):
    implements(IBrowserView, IPublishTraverse)

    def __init__(self, context, request, model):
        super(RemoveModelView, self).__init__(context, request)
        self.model = model

    @property
    def success_message(self):
        return _('msg_successfully_deleted',
                 default=u'The object was deleted successfully')

    def nextURL(self):
        raise NotImplementedError

    def __call__(self):
        if not self.model:
            raise NotFound
        if not self.model.is_removable():
            raise Unauthorized("Editing is not allowed")

        self.remove()

        api.portal.show_message(self.success_message, api.portal.get().REQUEST)
        return self.request.response.redirect(self.nextURL())

    def remove(self):
        session = create_session()
        session.delete(self.model)
