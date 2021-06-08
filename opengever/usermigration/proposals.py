from opengever.meeting.proposal import IBaseProposal
from opengever.usermigration.base import BasePloneObjectAttributesMigrator


class ProposalsMigrator(BasePloneObjectAttributesMigrator):

    fields_to_migrate = ('issuer',)
    interface_to_query = IBaseProposal
    interface_to_adapt = IBaseProposal
