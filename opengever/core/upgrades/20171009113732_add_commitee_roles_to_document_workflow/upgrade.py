from ftw.upgrade import UpgradeStep
from ftw.upgrade.helpers import update_security_for
from ftw.upgrade.workflow import WorkflowSecurityUpdater
from opengever.meeting.committeecontainer import ICommitteeContainer
from operator import methodcaller


class AddCommitteRolesToDocumentAndMailWorkflows(UpgradeStep):
    """Update the document- and mail-workflows so that it supports the
    opengever.meeting roles.

    Roles:
    - CommitteeAdministrator
    - CommitteeMember
    - CommitteeResponsible

    All those roles are only available on a commitee container or on a comittee,
    therefore only documents / mails within committee containers must be updated.

    The "Access contents information" permission must always be granted
    along with the "View" permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_documents_and_mails_in_commitee_containers()
        self.update_committee_roles()

    def update_documents_and_mails_in_commitee_containers(self):
        for obj in self.get_documents_and_mails_in_committee_containers():
            update_security_for(obj, reindex_security=True)

    def get_documents_and_mails_in_committee_containers(self):
        committee_container_brains = self.catalog_unrestricted_search(
            {'object_provides': ICommitteeContainer.__identifier__})

        if not committee_container_brains:
            return []

        query = {
            'paths': map(methodcaller('getPath'), committee_container_brains),
            'portal_type': WorkflowSecurityUpdater().get_suspected_types(
                ['opengever_document_workflow',
                 'opengever_mail_workflow'])
        }
        message = 'Update document- and mail-workflow in committee containers.'
        return self.objects(query, message)

    def update_committee_roles(self):
        """The roles which "CommitteeRoles" sets on the committees for the
        primary group have been changed.

        Before: CommitteeResponsible, Editor, Reader
        After: CommitteeResponsible
        """
        query = {'portal_type': 'opengever.meeting.committee'}
        msg = 'Update local roles of committees.'
        for committee in self.objects(query, msg):
            group_id = committee.load_model().group_id
            current_roles = dict(committee.get_local_roles()).get(group_id, ())
            new_roles = list(set(current_roles) - {'Editor', 'Reader'})
            committee.manage_setLocalRoles(group_id, new_roles)
            committee.reindexObjectSecurity()
