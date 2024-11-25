from opengever.base.model import Base
from opengever.base.model import UID_LENGTH
from opengever.base.model import UNIT_ID_LENGTH
from opengever.base.model import USER_ID_LENGTH
from opengever.base.types import JSONList
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.schema import PrimaryKeyConstraint


tables = [
    'local_roles',
]


class LocalRoles(Base):

    __tablename__ = 'local_roles'
    __table_args__ = (PrimaryKeyConstraint('admin_unit_id', 'principal_id', 'object_uid'), )

    admin_unit_id = Column(String(UNIT_ID_LENGTH), ForeignKey('admin_units.unit_id'), nullable=False)
    principal_id = Column(String(USER_ID_LENGTH), nullable=False)
    object_uid = Column(String(UID_LENGTH), nullable=False)
    roles = Column(JSONList(), nullable=True)

    def __repr__(self):
        return '<LocalRole {}, {}, {}>'.format(
            self.admin_unit_id, self.principal_id, self.object_uid)
