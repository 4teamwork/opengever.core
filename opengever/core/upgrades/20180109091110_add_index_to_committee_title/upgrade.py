from opengever.core.upgrade import SchemaMigration


class AddCommitteeTitleIndex(SchemaMigration):
    """Add index to committee title.
    """

    def migrate(self):
        self.op.create_index(
            'ix_committee_title',
            'committees',
            ['title'])
