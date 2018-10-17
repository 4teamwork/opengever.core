from opengever.ogds.models.group import Team
from opengever.ogds.models.tests.base import OGDSTestCase
from sqlalchemy.exc import IntegrityError


class TestTeam(OGDSTestCase):
    def test_title_is_required(self):
        team = Team(group=self.members_a, org_unit=self.org_unit_a)
        self.session.add(team)
        with self.assertRaises(IntegrityError):
            self.session.flush()

    def test_group_is_required(self):
        team = Team(title=u'Abteilung XY', org_unit=self.org_unit_a)
        self.session.add(team)
        with self.assertRaises(IntegrityError):
            self.session.flush()

    def test_org_unit_is_required(self):
        team = Team(title=u'Abteilung XY', group=self.members_a)
        self.session.add(team)
        with self.assertRaises(IntegrityError):
            self.session.flush()

    def test_creatable(self):
        team = Team(title=u'Abteilung XY', group=self.members_a, org_unit=self.org_unit_a)
        self.session.add(team)
        self.assertEqual(1, len(self.session.query(Team).all()))

    def test_is_active_by_default(self):
        team = Team(title=u'Abteilung XY', group=self.members_a, org_unit=self.org_unit_a)
        self.session.add(team)
        self.session.flush()
        self.assertTrue(team.active)

    def test_repr(self):
        team = Team(title=u'\xc4-Team', group=self.members_a, org_unit=self.org_unit_a)
        self.session.add(team)
        self.assertEqual("<Team u'\\xc4-Team' ('members_a')>", str(team))

    def test_actor_id_is_team_id_prefixed_with_team(self):
        team = Team(team_id=55, title=u'\xc4-Team', group=self.members_a, org_unit=self.org_unit_a)
        self.session.add(team)
        self.assertEqual('team:55', team.actor_id())

    def test_label(self):
        team = Team(title=u'\xc4-Team', group=self.members_a, org_unit=self.org_unit_a)
        self.session.add(team)
        self.assertEqual(u'\xc4-Team (Unit A)', team.label())

    def test_get_by_actor_id(self):
        team1 = Team(title=u'\xc4-Team', group=self.members_a, org_unit=self.org_unit_a)
        team2 = Team(title=u'\xc4-Team', group=self.members_a, org_unit=self.org_unit_a)
        self.session.add(team1)
        self.session.add(team2)
        self.assertEqual(team1, Team.query.get_by_actor_id('team:1'))
        self.assertEqual(team2, Team.query.get_by_actor_id('team:2'))

    def test_get_edit_values_handles_boolean_fields(self):
        team = Team(title=u'\xc4-Team', group=self.members_a, org_unit=self.org_unit_a, active=False)
        self.session.add(team)
        self.assertEqual({'title': u'\xc4-Team', 'active': False}, team.get_edit_values(['title', 'active']))
