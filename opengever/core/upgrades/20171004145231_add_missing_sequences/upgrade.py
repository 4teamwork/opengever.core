from opengever.core.upgrade import SchemaMigration


class AddMissingSequences(SchemaMigration):
    """Add missing sequences.
    """

    def migrate(self):
        known_sequences = (
            'activities_id_seq',
            'adresses_id_seq',
            'agendaitems_id_seq',
            'archived_address_id_seq',
            'archived_contact_id_seq',
            'archived_mail_address_id_seq',
            'archived_phonenumber_id_seq',
            'archived_url_id_seq',
            'committee_id_seq',
            'contacts_id_seq',
            'excerpts_id_seq',
            'generateddocument_id_seq',
            'locks_id_seq',
            'mail_adresses_id_seq',
            'meeting_id_seq',
            'member_id_seq',
            'membership_id_seq',
            'notification_defaults_id_seq',
            'notifications_id_seq',
            'org_roles_id_seq',
            'participation_roles_id_seq',
            'participations_id_seq',
            'periods_id_seq',
            'phonenumber_id_seq',
            'proposal_history_id_seq',
            'proposal_id_seq',
            'resources_id_seq',
            'submitteddocument_id_seq',
            'task_id_seq',
            'teams_id_seq',
            'urls_id_seq',
            'watchers_id_seq')
        map(self.ensure_sequence_exists, known_sequences)
