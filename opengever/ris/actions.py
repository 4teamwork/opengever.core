from opengever.base.context_actions import BaseContextActions
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.ris.proposal import IProposal
from plone import api
from zope.component import adapter


@adapter(IProposal, IOpengeverBaseLayer)
class RisProposalContextActions(BaseContextActions):
    def is_create_task_from_proposal_available(self):
        return api.user.has_permission('opengever.task: Add task', obj=self.context)
