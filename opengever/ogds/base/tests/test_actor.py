from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.contact.tests import create_contacts
from opengever.kub.testing import KUB_RESPONSES
from opengever.kub.testing import KuBIntegrationTestCase
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.actor import CommitteeActor
from opengever.ogds.base.actor import ContactActor
from opengever.ogds.base.actor import InboxActor
from opengever.ogds.base.actor import INTERACTIVE_ACTOR_CURRENT_USER_ID
from opengever.ogds.base.actor import INTERACTIVE_ACTOR_IDS
from opengever.ogds.base.actor import INTERACTIVE_ACTOR_RESPONSIBLE_ID
from opengever.ogds.base.actor import InteractiveActor
from opengever.ogds.base.actor import KuBContactActor
from opengever.ogds.base.actor import NullActor
from opengever.ogds.base.actor import OGDSGroupActor
from opengever.ogds.base.actor import OGDSUserActor
from opengever.ogds.base.actor import TeamActor
from opengever.ogds.models.user import User
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from unittest import TestCase
import json
import requests_mock


class TestActorLookup(IntegrationTestCase):

    def test_null_actor(self):
        actor = Actor.lookup('not-existing')
        self.assertIsInstance(actor, NullActor)
        self.assertEqual('Unknown ID (not-existing)', actor.get_label())
        self.assertIsNone(actor.get_profile_url())
        self.assertEqual('not-existing', actor.get_link())
        self.assertEqual(u'not-existing', actor.login_name)

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
        self.assertEqual(u'fa_inbox_users', actor.login_name)

    def test_contact_actor_lookup(self):
        create_contacts(self)
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

        self.assertEqual(None, actor.login_name)

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

        self.assertEqual(None, actor.login_name)

    def test_team_actor_lookup(self):
        self.login(self.regular_user)
        actor = Actor.lookup('team:1')

        self.assertIsInstance(actor, TeamActor)
        self.assertEqual(u'Projekt \xdcberbaung Dorfmatte (Finanz\xe4mt)',
                         actor.get_label())
        self.assertEqual(None,
                         actor.get_profile_url())
        self.assertEqual(
            u'<span class="actor-label actor-team">'
            u'Projekt \xdcberbaung Dorfmatte (Finanz\xe4mt)</span>',
            actor.get_link(with_icon=True))

        self.assertEqual(
            u'Projekt \xdcberbaung Dorfmatte (Finanz\xe4mt)',
            actor.get_link())

        self.assertEqual(None, actor.login_name)

    def test_team_profile_url_for_foreign_user(self):
        self.login(self.foreign_contributor)
        actor = Actor.lookup('team:1')
        self.assertEqual(
            u'Projekt \xdcberbaung Dorfmatte (Finanz\xe4mt)',
            actor.get_link())

    def test_user_actor_ogds_user(self):
        actor = Actor.lookup(self.secretariat_user.id)

        self.assertIsInstance(actor, OGDSUserActor)
        self.assertEqual(
            u'K\xf6nig J\xfcrgen (jurgen.konig)', actor.get_label())
        self.assertEqual(self.secretariat_user.id, actor.permission_identifier)
        self.assertTrue(
            actor.get_profile_url().endswith('@@user-details/%s' % self.secretariat_user.id))

        self.assertEqual(
            u'<a href="http://nohost/plone/@@user-details/%s">'
            u'K\xf6nig J\xfcrgen (jurgen.konig)</a>' % self.secretariat_user.id,
            actor.get_link())

        self.assertEqual(
            u'<a href="http://nohost/plone/@@user-details/%s" '
            u'class="actor-label actor-user">K\xf6nig J\xfcrgen '
            u'(jurgen.konig)</a>' % self.secretariat_user.id,
            actor.get_link(with_icon=True))

        self.assertEqual(self.secretariat_user.getUserName(), actor.login_name)

    def test_group_actor_lookup(self):
        self.login(self.regular_user)
        actor = Actor.lookup('projekt_a')

        self.assertIsInstance(actor, OGDSGroupActor)
        self.assertEqual(u'Projekt A',
                         actor.get_label())
        self.assertEqual('http://nohost/plone/@@list_groupmembers?group=projekt_a',
                         actor.get_profile_url())

        self.assertEqual(
            u'<a href="http://nohost/plone/@@list_groupmembers?group=projekt_a" '
            'class="actor-label actor-user">Projekt A</a>',
            actor.get_link(with_icon=True))

        self.assertEqual(
            u'<a href="http://nohost/plone/@@list_groupmembers?group=projekt_a">'
            'Projekt A</a>',
            actor.get_link())

        self.assertEqual(u'projekt_a', actor.login_name)

    def test_get_link_returns_safe_html(self):
        self.login(self.regular_user)

        user = User.get(self.regular_user.id)
        user.firstname = "Foo <b onmouseover=alert('Foo!')>click me!</b>"

        actor = Actor.lookup(self.regular_user.id)

        self.assertEquals(
            u'<a href="http://nohost/plone/@@user-details/%s">'
            u'B\xe4rfuss Foo &lt;b onmouseover=alert(&apos;Foo!&apos;)&gt;click me!&lt;/b&gt; (kathi.barfuss)'
            u'</a>' % self.regular_user.id,
            actor.get_link())

    def test_interactive_actor_lookup(self):
        self.login(self.regular_user)

        responsible_actor = Actor.lookup(INTERACTIVE_ACTOR_RESPONSIBLE_ID)
        self.assertIsInstance(responsible_actor, InteractiveActor)
        self.assertEqual('Responsible',
                         responsible_actor.get_label())
        self.assertEqual(None, responsible_actor.login_name)

        current_user_actor = Actor.lookup(INTERACTIVE_ACTOR_CURRENT_USER_ID)
        self.assertIsInstance(current_user_actor, InteractiveActor)
        self.assertEqual('Logged in user',
                         current_user_actor.get_label())
        self.assertEqual(None, current_user_actor.login_name)

    def test_interactive_actor_lookup_raises_an_error_for_unknown_actors(self):
        self.login(self.regular_user)

        unknown_interactive_actor = 'unknown'

        self.assertNotIn(unknown_interactive_actor, INTERACTIVE_ACTOR_IDS)

        with self.assertRaises(ValueError) as error:
            InteractiveActor(unknown_interactive_actor)

        self.assertEqual(
            'Interactive actor must be one of '
            'interactive_actor:responsible, interactive_actor:current_user',
            str(error.exception))


@requests_mock.Mocker()
class TestKuBContactActor(KuBIntegrationTestCase):

    def test_person_actor_lookup(self, mocker):
        self.mock_labels(mocker)
        url = self.mock_get_by_id(mocker, self.person_jean)
        self.login(self.regular_user)
        actor = Actor.lookup(self.person_jean)

        self.assertIsInstance(actor, KuBContactActor)
        self.assertEqual(u'Dupont Jean', actor.get_label())
        self.assertEqual(None, actor.get_profile_url())
        self.assertEqual(json.loads(json.dumps(KUB_RESPONSES[url])),
                         actor.represents().data)

    def test_organization_actor_lookup(self, mocker):
        self.mock_labels(mocker)
        url = self.mock_get_by_id(mocker, self.org_ftw)
        self.login(self.regular_user)
        actor = Actor.lookup(self.org_ftw)

        self.assertIsInstance(actor, KuBContactActor)
        self.assertEqual(u'4Teamwork', actor.get_label())
        self.assertEqual(None, actor.get_profile_url())
        self.assertEqual(KUB_RESPONSES[url], actor.represents().data)

    def test_membership_actor_lookup(self, mocker):
        self.mock_labels(mocker)
        url = self.mock_get_by_id(mocker, self.memb_jean_ftw)
        self.login(self.regular_user)
        actor = Actor.lookup(self.memb_jean_ftw)

        self.assertIsInstance(actor, KuBContactActor)
        self.assertEqual(u'Dupont Jean - 4Teamwork (CEO)', actor.get_label())
        self.assertEqual(None, actor.get_profile_url())
        self.assertEqual(KUB_RESPONSES[url], actor.represents().data)

    def test_kub_contact_actor_lookup_for_not_existing_contact(self, mocker):
        contact_id = "invalid-id"
        self.mock_get_by_id(mocker, contact_id)
        self.login(self.regular_user)
        actor = Actor.lookup(contact_id)

        self.assertIsInstance(actor, NullActor)

    @browsing
    def test_actors_response_for_kubcontact(self, mocker, browser):
        self.mock_labels(mocker)
        self.login(self.regular_user, browser=browser)
        url = "{}/@actors/{}".format(self.portal.absolute_url(), self.person_jean)
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        self.assertDictEqual(
            {
                u'@id': url,
                u'@type': u'virtual.ogds.actor',
                u'active': True,
                u'actor_type': u'kubcontact',
                u'identifier': self.person_jean,
                u'is_absent': False,
                u'label': u'Dupont Jean',
                u'login_name': None,
                u'portrait_url': None,
                u'representatives': [],
                u'represents': {
                    u'@id': u'http://nohost/plone/@kub/person:9af7d7cc-b948-423f-979f-587158c6bc65'
                }
            },
            browser.json)

    @browsing
    def test_full_representation_for_kubcontact(self, mocker, browser):
        self.mock_get_by_id(mocker, self.person_jean)
        self.mock_labels(mocker)
        self.login(self.regular_user, browser=browser)
        url = "{}/@actors/{}?full_representation=true".format(
            self.portal.absolute_url(), self.person_jean)
        browser.open(url, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertDictContainsSubset({
            u'@id': u'http://nohost/plone/@kub/person:9af7d7cc-b948-423f-979f-587158c6bc65',
            u'dateOfBirth': u'1992-05-15',
            u'fullName': u'Dupont Jean'}, browser.json['represents'])


class TestActorCorresponding(IntegrationTestCase):

    def test_user_corresponds_to_current_user(self):
        actor = Actor.lookup(self.secretariat_user.id)

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

    def test_group_corresponds_to_all_group_members(self):
        actor = Actor.lookup('projekt_a')

        self.assertTrue(
            actor.corresponds_to(self.get_ogds_user(self.regular_user)))
        self.assertTrue(
            actor.corresponds_to(self.get_ogds_user(self.dossier_responsible)))
        self.assertFalse(
            actor.corresponds_to(self.get_ogds_user(self.secretariat_user)))


class TestActorRepresentatives(IntegrationTestCase):

    def test_user_is_the_only_representatives_of_a_user(self):
        actor = Actor.lookup(self.secretariat_user.id)
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

    def test_all_group_members_are_group_representatives(self):
        actor = Actor.lookup('projekt_a')
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
