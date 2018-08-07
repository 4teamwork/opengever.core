from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.models.group import Team
from opengever.ogds.models.tests.base import OGDSTestCase
from sqlalchemy.exc import IntegrityError


class TestTeam(OGDSTestCase):

    def setUp(self):
        self.members = create(Builder('ogds_group')
                              .id('members'))
        self.admin_unit = create(Builder('admin_unit').id('fd'))
        self.org_unit = create(Builder('org_unit')
                               .id('unit')
                               .having(title='Unit A',
                                       admin_unit=self.admin_unit,
                                       users_group=self.members,
                                       inbox_group=self.members))

    def test_title_is_required(self):
        team = Team(group=self.members, org_unit=self.org_unit)
        self.session.add(team)
        with self.assertRaises(IntegrityError):
            self.session.commit()

    def test_group_is_required(self):
        team = Team(title=u'Abteilung XY', org_unit=self.org_unit)
        self.session.add(team)
        with self.assertRaises(IntegrityError):
            self.session.commit()

    def test_org_unit_is_required(self):
        team = Team(title=u'Abteilung XY', group=self.members)
        self.session.add(team)
        with self.assertRaises(IntegrityError):
            self.session.commit()

    def test_creatable(self):
        team = Team(title=u'Abteilung XY',
                    group=self.members,
                    org_unit=self.org_unit)
        self.session.add(team)
        self.session.commit()

        self.assertEquals(1, len(self.session.query(Team).all()))

    def test_is_active_by_default(self):
        team = Team(title=u'Abteilung XY',
                    group=self.members,
                    org_unit=self.org_unit)
        self.session.add(team)
        self.session.commit()

        self.assertTrue(team.active)

    def test_repr(self):
        team = Team(title=u'\xc4-Team',
                    group=self.members, org_unit=self.org_unit)
        self.session.add(team)
        self.assertEquals("<Team u'\\xc4-Team' ('members')>", str(team))

    def test_actor_id_is_team_id_prefixed_with_team(self):
        team = Team(team_id=55, title=u'\xc4-Team',
                    group=self.members, org_unit=self.org_unit)
        self.session.add(team)
        self.assertEquals('team:55', team.actor_id())

    def test_label(self):
        team = Team(title=u'\xc4-Team',
                    group=self.members, org_unit=self.org_unit)
        self.session.add(team)
        self.assertEquals(u'\xc4-Team (Unit A)', team.label())

    def test_get_by_actor_id(self):
        team1 = Team(title=u'\xc4-Team',
                     group=self.members, org_unit=self.org_unit)
        team2 = Team(title=u'\xc4-Team',
                     group=self.members, org_unit=self.org_unit)
        self.session.add(team1)
        self.session.add(team2)
        self.session.commit()

        self.assertEquals(team1, Team.query.get_by_actor_id('team:1'))
        self.assertEquals(team2, Team.query.get_by_actor_id('team:2'))

    def test_get_edit_values_handles_boolean_fields(self):
        team = Team(title=u'\xc4-Team',
                    group=self.members,
                    org_unit=self.org_unit,
                    active=False)

        self.session.add(team)
        self.session.commit()

        self.assertEquals(
            {'title': u'\xc4-Team', 'active': False},
            team.get_edit_values(['title', 'active']))
