from itertools import cycle
from opengever.base.model import create_session
from opengever.ogds.models.group import Group
from opengever.ogds.models.org_unit import OrgUnit
from opengever.ogds.models.team import Team


class TeamExampleContentCreator(object):
    """Create Teams for example content.

    Creates one team per group.

    Predictably cycles through the existing org units.
    """

    def __init__(self):
        self.db_session = create_session()

    def create(self):
        org_units = cycle(OrgUnit.query.all())
        groups = Group.query.filter_by(active=True).all()
        for group in groups:
            team = Team(title=group.title or group.groupid, group=group, org_unit=next(org_units))
            self.db_session.add(team)
