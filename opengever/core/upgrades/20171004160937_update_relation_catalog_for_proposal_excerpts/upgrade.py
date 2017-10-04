from ftw.upgrade import UpgradeStep
from opengever.meeting import is_word_meeting_implementation_enabled
from z3c.relationfield.event import addRelations


class UpdateRelationCatalogForProposalExcerpts(UpgradeStep):
    """Register excerpt relations of submitted proposals in relation catalog.
    """

    def __call__(self):
        self.install_upgrade_profile()
        if is_word_meeting_implementation_enabled():
            query = {'object_provides': 'opengever.meeting.proposal.ISubmittedProposal'}
            for obj in self.objects(query, self.__class__.__doc__):
                addRelations(obj, None)
