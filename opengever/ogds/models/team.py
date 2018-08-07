from opengever.ogds.models import BASE
from opengever.ogds.models import GROUP_ID_LENGTH
from opengever.ogds.models import UNIT_ID_LENGTH
from opengever.ogds.models import UNIT_TITLE_LENGTH
from opengever.ogds.models.query import BaseQuery
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence


TEAM_ACTOR_PREFIX = u'team'


class TeamQuery(BaseQuery):

    searchable_fields = ['title']

    def get_by_actor_id(self, value):
        prefix, team_id = value.split(':')

        if prefix != TEAM_ACTOR_PREFIX:
            raise ValueError(
                '{} is not a valid team actor id, expect '
                'smth like `team:135`'.format(value))

        return self.filter_by(team_id=team_id).one()


class Team(BASE):
    """Team model.

    A team can be used as a task responsible when assigning a task to a group.
    """

    query_cls = TeamQuery

    __tablename__ = 'teams'

    team_id = Column('id', Integer, Sequence('teams_id_seq'), primary_key=True)
    title = Column(String(UNIT_TITLE_LENGTH), nullable=False)
    active = Column(Boolean, default=True)
    groupid = Column(String(GROUP_ID_LENGTH),
                     ForeignKey('groups.groupid'), nullable=False)
    group = relationship("Group", back_populates="teams")
    org_unit_id = Column(String(UNIT_ID_LENGTH),
                         ForeignKey('org_units.unit_id'), nullable=False)
    org_unit = relationship("OrgUnit", back_populates="teams")

    def __repr__(self):
        return '<Team {!r} ({!r})>'.format(self.title, self.group.groupid)

    def actor_id(self):
        return u'{}:{}'.format(TEAM_ACTOR_PREFIX, self.team_id)

    def label(self):
        return u'{} ({})'.format(self.title, self.org_unit.title)

    # TODO: the following methods should be removed when moving
    # opengever.ogds.models to opengever.core and inherit from
    # `opengever.base.model.SQLFormSupport` instead.

    def is_editable_by_current_user(self, container):
        return False

    def is_editable(self):
        return True

    def get_edit_values(self, fieldnames):
        _marker = object()

        values = {}
        for fieldname in fieldnames:
            value = getattr(self, fieldname, _marker)
            if value is _marker:
                continue

            values[fieldname] = value
        return values

    def get_edit_url(self, context):
        return self.get_url(context, view='edit')

    def update_model(self, data):
        for key, value in data.items():
            setattr(self, key, value)
