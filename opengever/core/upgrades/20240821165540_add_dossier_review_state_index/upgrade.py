from ftw.upgrade import UpgradeStep
from opengever.core.upgrade import NightlyIndexer


class AddDossierReviewStateIndex(UpgradeStep):
    """Add dossier review state index.
    """

    def __call__(self):
        query = {'portal_type': [
            'opengever.dossier.businesscasedossier',
            'opengever.meeting.proposal',
            'opengever.ris.proposal',
            'opengever.document.document',
            'opengever.task.task',
            'opengever.private.dossier',
            'ftw.mail.mail',
            'opengever.meeting.meetingdossier'
        ]}

        with NightlyIndexer(idxs=["dossier_review_state"],
                            index_in_solr_only=True) as indexer:
            for brain in self.brains(query, 'Index dossier_review_state in Solr'):
                indexer.add_by_brain(brain)
