from opengever.core.upgrade import SchemaMigration
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import table
import itertools


meeting_excerpts_table = table(
    'meeting_excerpts',
    column('meeting_id'),
    column('document_id'),
)


generateddocuments_table = table(
    'generateddocuments',
    column('id'),
)


class DropMeetingExcerptsTableAndEntries(SchemaMigration):
    """Drop meeting_excerpts table and entries in generateddocuments.

    The meeting_excerpts table used to track so called "manual" excerpts that
    could be generated for multiple proposals and with a custom set of fields.

    This functionality has been removed. The old exceprts will remain a
    document in the meeting dossier though, so no information is lost by
    removing the secondary table and the entries in generateddocuments.
    """
    def migrate(self):
        ids_to_delete = self.get_generated_document_ids_to_delete()
        self.op.drop_table('meeting_excerpts')
        self.delete_generated_documents(ids_to_delete)

    def delete_generated_documents(self, ids_to_delete):
        if not ids_to_delete:
            return

        del_statement = generateddocuments_table.delete().where(
            generateddocuments_table.c.id.in_(ids_to_delete))
        self.execute(del_statement)

    def get_generated_document_ids_to_delete(self):
        statement = select([meeting_excerpts_table.c.document_id])
        result_rows = list(self.execute(statement).fetchall())

        ids_to_delete = set(itertools.chain(*result_rows))
        return ids_to_delete
