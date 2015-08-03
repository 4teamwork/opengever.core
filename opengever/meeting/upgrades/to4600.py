from opengever.core.upgrade import SchemaMigration


class DropPreProtocol(SchemaMigration):

    profileid = 'opengever.meeting'
    upgradeid = 4600

    def migrate(self):
        self.drop_pre_protocol_column_from_meeting()

    def drop_pre_protocol_column_from_meeting(self):
        self.op.drop_column('meetings', 'pre_protocol_document_id')
