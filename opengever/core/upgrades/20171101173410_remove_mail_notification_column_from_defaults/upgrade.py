from opengever.core.upgrade import SchemaMigration


class RemoveMailNotificationColumnFromDefaults(SchemaMigration):
    """Remove mail_notification column from defaults.
    """

    def migrate(self):
        self.op.drop_column('notification_defaults', 'mail_notification')
