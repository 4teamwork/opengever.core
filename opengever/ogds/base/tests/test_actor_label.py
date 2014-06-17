from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.actor import ContactActor
from opengever.ogds.base.actor import InboxActor
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from unittest import TestCase


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
