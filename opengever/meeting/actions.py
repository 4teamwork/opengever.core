from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.base.listing_actions import BaseListingActions


class ProposalListingActions(BaseListingActions):

    def is_export_proposals_available(self):
        return True
