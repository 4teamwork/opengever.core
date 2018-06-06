from ftw.upgrade import UpgradeStep
from plone import api
from z3c.relationfield.event import addRelations


class UpdateRelationCatalogForProposalExcerpts(UpgradeStep):
    """Register excerpt relations of submitted proposals in relation catalog.
    """

    def __call__(self):
        self.install_upgrade_profile()
        has_meeting_feature = api.portal.get_registry_record(
            'opengever.meeting.interfaces.IMeetingSettings.is_feature_enabled')
        if has_meeting_feature:
            query = {'object_provides': 'opengever.meeting.proposal.ISubmittedProposal'}
            for obj in self.objects(query, self.__class__.__doc__):
                addRelations(obj, None)
