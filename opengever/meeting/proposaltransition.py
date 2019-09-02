from opengever.base.transition import ITransitionExtender
from opengever.base.transition import TransitionExtender
from opengever.meeting import _
from opengever.meeting.interfaces import IHistory
from opengever.meeting.proposal import IProposal
from opengever.meeting.proposalsqlsyncer import ProposalSqlSyncer
from plone.supermodel.model import Schema
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


class IText(Schema):

    text = schema.Text(
        title=_('label_comment', default="Comment"),
        required=False,
        )


@implementer(ITransitionExtender)
@adapter(IProposal, IBrowserRequest)
class CancelTransitionExtender(TransitionExtender):

    schemas = [IText, ]

    def after_transition_hook(self, transition, disable_sync, transition_params):
        IHistory(self.context).append_record(
            u'cancelled', text=transition_params.get('text'))
        ProposalSqlSyncer(self.context, None).sync()


@implementer(ITransitionExtender)
@adapter(IProposal, IBrowserRequest)
class ReactivateTransitionExtender(TransitionExtender):

    schemas = [IText, ]

    def after_transition_hook(self, transition, disable_sync, transition_params):
        IHistory(self.context).append_record(
            u'reactivated', text=transition_params.get('text'))
        ProposalSqlSyncer(self.context, None).sync()
