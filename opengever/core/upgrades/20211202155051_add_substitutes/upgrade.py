from opengever.base.model import USER_ID_LENGTH
from opengever.core.upgrade import SchemaMigration
from opengever.ogds.models.user import User
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.schema import Sequence


class AddSubstitutes(SchemaMigration):
    """Add substitutes.
    """

    def migrate(self):
        self.op.create_table(
            'substitutes',
            Column("id", Integer, Sequence("substitution_id_seq"), primary_key=True),
            Column('userid', String(USER_ID_LENGTH), ForeignKey(User.userid)),
            Column('substitute_userid', String(USER_ID_LENGTH), ForeignKey(User.userid))
            )

        self.ensure_sequence_exists('substitution_id_seq')

        self.op.add_column('users', Column('absent', Boolean, default=False))
        self.op.add_column('users', Column('absent_from', Date))
        self.op.add_column('users', Column('absent_to', Date))
