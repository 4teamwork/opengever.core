from opengever.base.transition import ITransitionExtender
from opengever.inbox.forwarding import IForwarding
from opengever.task.interfaces import IYearfolderStorer
from opengever.task.transition import DefaultTransitionExtender
from opengever.task.util import add_simple_response
from zope.component import adapter
from zope.interface import implementer


@implementer(ITransitionExtender)
@adapter(IForwarding)
class ForwardingDefaultTransitionExtender(DefaultTransitionExtender):
    """Default transiition extender for all forwarding transitions."""


@implementer(ITransitionExtender)
@adapter(IForwarding)
class ForwardingCloseTransitionExtender(ForwardingDefaultTransitionExtender):
    """Transition Extender for forwardings close transition,
    """

    def after_transition_hook(self, transition, disable_sync, **kwargs):
        add_simple_response(
            self.context, transition=transition, text=kwargs.get('text'))

        IYearfolderStorer(self.context).store_in_yearfolder()
