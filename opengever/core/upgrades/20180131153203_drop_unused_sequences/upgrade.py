from opengever.core.upgrade import SchemaMigration


class DropUnusedSequences(SchemaMigration):
    """DISABLED: Drop unused sequences."""

    def migrate(self):
        # This upgrade is disabled because it failed when deploying on TEST,
        # indicating that at least the 'subscriptions_resource_id_seq'
        # sequence was still being used.
        return
