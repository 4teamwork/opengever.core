from opengever.core.upgrade import SchemaMigration


class DropPreProtocol(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4600

    def migrate(self):
        self.drop_pre_protocol_column_from_meeting()

    def drop_pre_protocol_column_from_meeting(self):
        fk_name = self.get_foreign_key_name(
            'meetings', 'pre_protocol_document_id')
        self.op.drop_constraint(fk_name, 'meetings', type_='foreignkey')
        self.op.drop_column('meetings', 'pre_protocol_document_id')
