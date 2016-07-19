from ftw.upgrade import UpgradeStep
from opengever.meeting.committeecontainer import ICommitteeContainer
from plone import api


class FixBeadcrumbsForCommitteesAndTheirContent(UpgradeStep):
    """Fix beadcrumbs for committees and their content.
    """

    indexes = ['Title', 'sortable_title']

    def __call__(self):
        self.reindex_content_inside_commitee_container()
        self.reindex_proposals_in_dossiers()

    def reindex_content_inside_commitee_container(self):
        container_brains = api.content.find(object_provides=ICommitteeContainer)
        if not container_brains:
            return

        assert len(container_brains) == 1, 'can have at most one container'
        container = container_brains[0]

        self.catalog_reindex_objects(
            {'path': container.getPath()},
            idxs=self.indexes
        )

    def reindex_proposals_in_dossiers(self):
        self.catalog_reindex_objects(
            {'object_provides': 'opengever.meeting.proposal.IProposal'},
            idxs=self.indexes
        )
