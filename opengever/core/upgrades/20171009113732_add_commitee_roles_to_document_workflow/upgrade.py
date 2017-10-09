from ftw.upgrade import UpgradeStep
from ftw.upgrade.helpers import update_security_for
from ftw.upgrade.workflow import WorkflowSecurityUpdater
from opengever.meeting.committeecontainer import ICommitteeContainer
from operator import methodcaller


class AddCommitteRolesToDocumentWorkflow(UpgradeStep):
    """Update the document workflow so that it supports the opengever.meeting roles.

    Roles:
    - CommitteeAdministrator
    - CommitteeMember
    - CommitteeResponsible

    All those roles are only available on a commitee container or on a comittee,
    therefore only documents within committee containers must be updated.

    The "Access contents information" permission must always be granted
    along with the "View" permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_documents_in_commitee_containers()

    def update_documents_in_commitee_containers(self):
        for document in self.get_documents_in_committee_containers():
            update_security_for(document, reindex_security=True)

    def get_documents_in_committee_containers(self):
        committee_container_brains = self.catalog_unrestricted_search(
            {'object_provides': ICommitteeContainer.__identifier__})
        query = {
            'paths': map(methodcaller('getPath'), committee_container_brains),
            'portal_type': WorkflowSecurityUpdater().get_suspected_types(
                ['opengever_document_workflow'])
        }
        message = 'Update document workflow in committee containers.'
        return self.objects(query, message)
