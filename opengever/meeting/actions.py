from opengever.base.context_actions import BaseContextActions
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.listing_actions import BaseListingActions
from opengever.meeting import is_meeting_feature_enabled
from opengever.meeting.proposal import IProposal
from opengever.meeting.proposal import ISubmittedProposal
from plone import api
from zope.component import adapter


class ProposalListingActions(BaseListingActions):

    def is_export_proposals_available(self):
        return True


@adapter(IProposal, IOpengeverBaseLayer)
class ProposalContextActions(BaseContextActions):

    def is_create_task_from_proposal_available(self):
        if ISubmittedProposal.providedBy(self.context):
            return False
        return api.user.has_permission('opengever.task: Add task',
                                       obj=self.context)

    def is_submit_additional_documents_available(self):
        if not api.user.has_permission('opengever.meeting: Add Proposal', obj=self.context):
            return False
        return is_meeting_feature_enabled() and \
            self.context.is_submit_additional_documents_allowed()
