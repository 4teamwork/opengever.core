from opengever.ogds.models import BASE
from opengever.ogds.models import GROUP_ID_LENGTH
from opengever.ogds.models import UNIT_ID_LENGTH
from opengever.ogds.models import UNIT_TITLE_LENGTH
from opengever.ogds.models.group import Group
from opengever.ogds.models.inbox import Inbox
from opengever.ogds.models.query import BaseQuery
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import relationship


class MultipleOrgUnitsStrategy(object):

    def prefix_label(self, org_unit, label):
        return u'{0} / {1}'.format(org_unit.label(), label)

    @property
    def is_inboxgroup_agency_active(self):
        return True


class LoneOrgUnitStrategy(object):

    def prefix_label(self, org_unit, label):
        return label

    @property
    def is_inboxgroup_agency_active(self):
        return False


class OrgUnitQuery(BaseQuery):

    searchable_fields = ['unit_id', 'title']


class OrgUnit(BASE):

    __tablename__ = 'org_units'

    query_cls = OrgUnitQuery

    unit_id = Column(String(UNIT_ID_LENGTH), primary_key=True)
    title = Column(String(UNIT_TITLE_LENGTH))
    enabled = Column(Boolean(), default=True)

    # formerly 'group'
    users_group_id = Column(String(GROUP_ID_LENGTH),
                            ForeignKey('groups.groupid'),
                            nullable=False)
    users_group = relationship(
        "Group",
        backref='org_unit_group',
        primaryjoin=users_group_id == Group.groupid)

    inbox_group_id = Column(String(GROUP_ID_LENGTH),
                            ForeignKey('groups.groupid'),
                            nullable=False)
    inbox_group = relationship(
        "Group",
        backref='inbox_group',
        primaryjoin=inbox_group_id == Group.groupid)

    admin_unit_id = Column(String(UNIT_ID_LENGTH),
                           ForeignKey('admin_units.unit_id'),
                           nullable=False)

    teams = relationship("Team", back_populates="org_unit")

    def __init__(self, unit_id, **kwargs):
        self.unit_id = unit_id
        self._chosen_strategy = None
        super(OrgUnit, self).__init__(**kwargs)

    def __repr__(self):
        return '<OrgUnit %s>' % self.id()

    def __eq__(self, other):
        if isinstance(other, OrgUnit):
            return self.id() == other.id()
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    @property
    def _strategy(self):
        if not hasattr(self, '_chosen_strategy') or \
                self._chosen_strategy is None:
            if self.query.count() > 1:
                self._chosen_strategy = MultipleOrgUnitsStrategy()
            else:
                self._chosen_strategy = LoneOrgUnitStrategy()
        return self._chosen_strategy

    def assigned_users(self):
        return self.users_group.users if self.users_group else []

    def id(self):
        return self.unit_id

    def label(self):
        return self.title

    def assign_to_admin_unit(self, admin_unit):
        self.admin_unit = admin_unit

    def inbox(self):
        return Inbox(self)

    def prefix_label(self, label):
        return self._strategy.prefix_label(self, label)

    @property
    def is_inboxgroup_agency_active(self):
        return self._strategy.is_inboxgroup_agency_active
