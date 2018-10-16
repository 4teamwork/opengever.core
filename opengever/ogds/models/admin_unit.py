from opengever.ogds.models import BASE
from opengever.ogds.models import UNIT_ID_LENGTH
from opengever.ogds.models import UNIT_TITLE_LENGTH
from opengever.ogds.models.group import groups_users
from opengever.ogds.models.org_unit import OrgUnit
from opengever.ogds.models.user import User
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import exists
from sqlalchemy import literal
from sqlalchemy import String
from sqlalchemy.orm import relationship


class AdminUnit(BASE):

    __tablename__ = 'admin_units'

    unit_id = Column(String(UNIT_ID_LENGTH), primary_key=True)
    title = Column(String(UNIT_TITLE_LENGTH))
    enabled = Column(Boolean(), default=True)
    ip_address = Column(String(50), nullable=False)
    site_url = Column(String(100), nullable=False)
    public_url = Column(String(100), nullable=False)
    abbreviation = Column(String(50), nullable=False)

    org_units = relationship("OrgUnit", backref="admin_unit")

    def __init__(self, unit_id, **kwargs):
        self.unit_id = unit_id
        super(AdminUnit, self).__init__(**kwargs)

    def __repr__(self):
        return '<AdminUnit %s>' % self.unit_id

    def __eq__(self, other):
        if isinstance(other, AdminUnit):
            return self.id() == other.id()
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def id(self):
        return self.unit_id

    def label(self):
        return self.title or u''

    def assigned_users(self):
        return self.session.query(User).filter(
            User.userid == groups_users.columns.userid).filter(
            groups_users.columns.groupid == OrgUnit.users_group_id).filter(
            OrgUnit.admin_unit_id == self.unit_id).all()

    def is_user_assigned(self, user):
        if user is None:
            # There might not be a corresponding OGDS user
            return False

        return self.session.query(literal(True)).filter(exists().where(
            OrgUnit.admin_unit_id == self.unit_id).where(
            OrgUnit.users_group_id == groups_users.columns.groupid).where(
            groups_users.columns.userid == user.userid)).scalar()

    def prefix_label(self, label):
        return u'{0} / {1}'.format(self.label(), label)
