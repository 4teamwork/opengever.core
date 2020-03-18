from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.actor import CommitteeActor
from opengever.ogds.base.actor import ContactActor
from opengever.ogds.base.actor import InboxActor
from opengever.ogds.base.actor import NullActor
from opengever.ogds.base.actor import OGDSUserActor
from opengever.ogds.base.actor import TeamActor
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from unittest import TestCase


class TestActorLookup(IntegrationTestCase):

    def test_null_actor(self):
        actor = Actor.lookup('not-existing')
        self.assertIsInstance(actor, NullActor)
        self.assertEqual('not-existing', actor.get_label())
        self.assertIsNone(actor.get_profile_url())
        self.assertEqual('not-existing', actor.get_link())

    def test_inbox_actor_lookup(self):
        actor = Actor.lookup('inbox:fa')

        self.assertIsInstance(actor, InboxActor)
        self.assertEqual(u'Inbox: Finanz\xe4mt', actor.get_label())
        self.assertIsNone(actor.get_profile_url())
        self.assertEqual(u'Inbox: Finanz\xe4mt', actor.get_link())
        self.assertEqual(u'fa_inbox_users', actor.permission_identifier)
        self.assertEqual(
            u'<span class="actor-label actor-inbox">Inbox: Finanz\xe4mt</span>',
            actor.get_link(with_icon=True))

    def test_contact_actor_lookup(self):
        self.login(self.regular_user)
        actor = Actor.lookup('contact:{}'.format(self.franz_meier.id))

        self.assertIsInstance(actor, ContactActor)
        self.assertEqual('Meier Franz (meier.f@example.com)',
                         actor.get_label())
        self.assertEqual(self.franz_meier.absolute_url(),
                         actor.get_profile_url())

        link = actor.get_link(with_icon=True)
        self.assertIn(actor.get_label(), link)
        self.assertIn(actor.get_profile_url(), link)
        self.assertIn('class="actor-label actor-contact"', link)

    def test_committee_actor_lookup(self):
        self.login(self.meeting_user)
        actor = Actor.lookup('committee:1')

        self.assertIsInstance(actor, CommitteeActor)
        self.assertEqual(u'Rechnungspr\xfcfungskommission',
                         actor.get_label())
        self.assertEqual(self.committee.absolute_url(),
                         actor.get_profile_url())

        self.assertEqual(
            u'<a href="{}" class="actor-label actor-committee">'
            u'Rechnungspr\xfcfungskommission'
            u'</a>'.format(self.committee.absolute_url()),
            actor.get_link(with_icon=True))

        self.assertEqual(
            u'<a href="{}">'
            u'Rechnungspr\xfcfungskommission'
            u'</a>'.format(self.committee.absolute_url()),
            actor.get_link(with_icon=False))

    def test_team_actor_lookup(self):
        self.login(self.regular_user)
        actor = Actor.lookup('team:1')

        self.assertIsInstance(actor, TeamActor)
        self.assertEqual(u'Projekt \xdcberbaung Dorfmatte (Finanz\xe4mt)',
                         actor.get_label())
        self.assertEqual('http://nohost/plone/kontakte/team-1/view',
                         actor.get_profile_url())

        self.assertEqual(
            u'<a href="http://nohost/plone/kontakte/team-1/view" '
            u'class="actor-label actor-team">Projekt \xdcberbaung Dorfmatte '
            u'(Finanz\xe4mt)</a>',
            actor.get_link(with_icon=True))

        self.assertEqual(
            u'<a href="http://nohost/plone/kontakte/team-1/view">'
            u'Projekt \xdcberbaung Dorfmatte (Finanz\xe4mt)</a>',
            actor.get_link())

    def test_team_profile_url_for_foreign_user(self):
        self.login(self.foreign_contributor)
        actor = Actor.lookup('team:1')
        self.assertEqual(
            u'<a href="http://nohost/plone/kontakte/team-1/view">'
            u'Projekt \xdcberbaung Dorfmatte (Finanz\xe4mt)</a>',
            actor.get_link())

    def test_user_actor_ogds_user(self):
        actor = Actor.lookup('jurgen.konig')

        self.assertIsInstance(actor, OGDSUserActor)
        self.assertEqual(
            u'K\xf6nig J\xfcrgen (jurgen.konig)', actor.get_label())
        self.assertEqual('jurgen.konig', actor.permission_identifier)
        self.assertTrue(
            actor.get_profile_url().endswith('/kontakte/user-jurgen.konig'))

        self.assertEqual(
            u'<a href="http://nohost/plone/kontakte/user-jurgen.konig/view">'
            u'K\xf6nig J\xfcrgen (jurgen.konig)</a>',
            actor.get_link())

        self.assertEqual(
            u'<a href="http://nohost/plone/kontakte/user-jurgen.konig/view" '
            u'class="actor-label actor-user">K\xf6nig J\xfcrgen '
            u'(jurgen.konig)</a>',
            actor.get_link(with_icon=True))

    def test_get_link_returns_safe_html(self):
        self.login(self.regular_user)

        self.franz_meier.firstname = u"Foo <b onmouseover=alert('Foo!')>click me!</b>"
        self.franz_meier.reindexObject()
        actor = Actor.lookup('contact:meier-franz')

        self.assertEquals(
            u'<a href="http://nohost/plone/kontakte/meier-franz">'
            u'Meier Foo &lt;b onmouseover=alert(&apos;Foo!&apos;)&gt;click me!&lt;/b&gt; (meier.f@example.com)'
            u'</a>',
            actor.get_link())


class TestActorCorresponding(IntegrationTestCase):

    def test_user_corresponds_to_current_user(self):
        actor = Actor.lookup('jurgen.konig')

        self.assertTrue(
            actor.corresponds_to(self.get_ogds_user(self.secretariat_user)))
        self.assertFalse(
            actor.corresponds_to(self.get_ogds_user(self.regular_user)))

    def test_inbox_corresponds_to_all_inbox_assigned_users(self):
        actor = Actor.lookup('inbox:fa')

        self.assertTrue(
            actor.corresponds_to(self.get_ogds_user(self.secretariat_user)))
        self.assertFalse(
            actor.corresponds_to(self.get_ogds_user(self.regular_user)))

    def test_team_corresponds_to_all_team_group_members(self):
        actor = Actor.lookup('team:1')

        self.assertTrue(
            actor.corresponds_to(self.get_ogds_user(self.regular_user)))
        self.assertTrue(
            actor.corresponds_to(self.get_ogds_user(self.dossier_responsible)))
        self.assertFalse(
            actor.corresponds_to(self.get_ogds_user(self.secretariat_user)))

    def test_committee_corresponds_to_users_in_responsible_group(self):
        actor = Actor.lookup('committee:1')

        self.assertTrue(
            actor.corresponds_to(self.get_ogds_user(self.committee_responsible)))
        self.assertTrue(
            actor.corresponds_to(self.get_ogds_user(self.administrator)))
        self.assertFalse(
            actor.corresponds_to(self.get_ogds_user(self.regular_user)))
        self.assertFalse(
            actor.corresponds_to(self.get_ogds_user(self.dossier_responsible)))


class TestActorRepresentatives(IntegrationTestCase):

    def test_user_is_the_only_representatives_of_a_user(self):
        actor = Actor.lookup('jurgen.konig')
        self.assertEquals([self.get_ogds_user(self.secretariat_user)],
                          actor.representatives())

        actor = Actor.lookup(self.regular_user.getId())
        self.assertEquals([self.get_ogds_user(self.regular_user)],
                          actor.representatives())

    def test_all_users_of_the_inbox_group_are_inbox_representatives(self):
        actor = Actor.lookup('inbox:fa')
        self.assertItemsEqual(
            [self.get_ogds_user(self.secretariat_user)],
            actor.representatives())

    def test_contact_has_no_representatives(self):
        actor = Actor.lookup('contact:meier-franz')
        self.assertItemsEqual([], actor.representatives())

    def test_all_group_members_are_team_representatives(self):
        actor = Actor.lookup('team:1')
        self.assertItemsEqual(
            [self.get_ogds_user(self.regular_user),
             self.get_ogds_user(self.dossier_responsible)],
            actor.representatives())

    def test_all_users_of_the_responsible_group_are_committee_representatives(self):
        actor = Actor.lookup('committee:1')
        self.assertItemsEqual(
            [self.get_ogds_user(self.committee_responsible),
             self.get_ogds_user(self.administrator)],
            actor.representatives())


class TestActorPermissionIdentifier(IntegrationTestCase):

    def test_groupid_is_team_actors_permission_identifier(self):
        actor = Actor.lookup('team:1')

        self.assertEquals('projekt_a', actor.permission_identifier)


class TestContactLabel(TestCase):

    class MockContact(object):
        def __init__(self):
            self.firstname = None
            self.lastname = None
            self.id = None
            self.email = None

    def setUp(self):
        self.contact = self.MockContact()
        self.actor = ContactActor('hp.meier', contact=self.contact)

    def test_contact_label_firstname_and_lastname(self):
        self.contact.firstname = 'Hanspeter'
        self.contact.lastname = 'Meier'
        self.contact.id = 'hp.meier'

        self.assertEqual('Meier Hanspeter', self.actor.get_label())

    def test_contact_label_lastname(self):
        self.contact.lastname = 'Meier'
        self.contact.id = 'hp.meier'

        self.assertEqual('Meier', self.actor.get_label())

    def test_contact_label_firstname(self):
        self.contact.firstname = 'Hanspeter'
        self.contact.id = 'hp.meier'

        self.assertEqual('Hanspeter', self.actor.get_label())

    def test_contact_label_id(self):
        self.contact.id = 'hp.meier'

        self.assertEqual('hp.meier', self.actor.get_label())

    def test_get_label_with_principal(self):
        self.contact.firstname = 'Hanspeter'
        self.contact.lastname = 'Meier'
        self.contact.id = 'hp.meier'
        self.contact.email = 'foo@example.com'

        self.assertEqual('Meier Hanspeter (foo@example.com)',
                         self.actor.get_label())
        self.assertEqual('Meier Hanspeter',
                         self.actor.get_label(with_principal=False))


class TestUserLabel(FunctionalTestCase):
    use_default_fixture = False

    def setUp(self):
        super(TestUserLabel, self).setUp()
        self.ogds_user = create(Builder('ogds_user')
                                .id('hans.muster')
                                .having(firstname=u'hans',
                                        lastname=u'muster'))

    def test_plone_user_label_integration(self):
        self.assertEqual(TEST_USER_NAME,
                         Actor.lookup(TEST_USER_ID).get_label(
                            with_principal=False))
        self.assertEqual("{} ({})".format(TEST_USER_NAME, TEST_USER_ID),
                         Actor.lookup(TEST_USER_ID).get_label())

    def test_ogds_user_label_integration(self):
        self.assertEqual(self.ogds_user.label(),
                         Actor.lookup('hans.muster').get_label())


class TestInboxLabel(TestCase):

    class MockOrgUnit(object):

        def label(self):
            return 'Poscht isch da'

    def setUp(self):
        self.org_unit = self.MockOrgUnit()
        self.actor = InboxActor('some_inbox', org_unit=self.org_unit)

    def test_get_label(self):
        self.assertEqual(u'Inbox: Poscht isch da', self.actor.get_label())
