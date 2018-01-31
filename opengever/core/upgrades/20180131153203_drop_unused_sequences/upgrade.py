from opengever.core.upgrade import SchemaMigration
from sqlalchemy.schema import DropSequence
from sqlalchemy.schema import Sequence


class DropUnusedSequences(SchemaMigration):
    """Drop unused sequences."""

    def migrate(self):
        # We'll only attempt to do this for postgresql
        if self.is_postgres:
            sequences_to_drop = (
                'proposal_history_id_seq',
                'subscriptions_resource_id_seq',
                )

            matching_sequences = tuple(
                Sequence(sequence['relname'])
                for sequence in self.execute(
                    "select relname from pg_class "
                    "where relkind = 'S' "
                    "and relname in {}"
                    .format(sequences_to_drop)
                    ).fetchall()
                )

            for sequence in matching_sequences:
                self.execute(DropSequence(sequence))
