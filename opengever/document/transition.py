from opengever.base.transition import ITransitionExtender
from opengever.base.transition import TransitionExtender
from opengever.document.document import IDocumentSchema
from plone import api
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


@implementer(ITransitionExtender)
@adapter(IDocumentSchema, IBrowserRequest)
class DocumentFinalizeTransitionExtender(TransitionExtender):

    def after_transition_hook(self, transition, disable_sync, transition_params):
        """Set finalizer
        """
        IDocumentSchema(self.context).finalizer = api.user.get_current().getId()
