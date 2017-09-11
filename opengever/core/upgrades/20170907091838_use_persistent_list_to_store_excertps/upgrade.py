from ftw.upgrade import UpgradeStep
from persistent.list import PersistentList


class UsePersistentListToStoreExcertps(UpgradeStep):
    """Use PersistentList to store excertps.
    """

    def __call__(self):
        self.install_upgrade_profile()

        msg = 'Use PersistentList for excerpts relation.'
        query = {'portal_type': 'opengever.meeting.submittedproposal'}

        for submitted_proposal in self.objects(query, msg):
            excerpt_list = getattr(submitted_proposal, 'excerpts', None)
            if not excerpt_list:
                continue

            submitted_proposal.excerpts = PersistentList(excerpt_list)
