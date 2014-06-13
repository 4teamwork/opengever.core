from opengever.ogds.base.actor import _OGDSUser
from opengever.ogds.base.actor import _PloneUser
from opengever.ogds.base.actor import ContactActor
from opengever.ogds.base.actor import InboxActor
from opengever.ogds.base.actor import UserActor
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


class TestPloneUserLabel(TestCase):

    class MockUser(object):
        def __init__(self):
            self.firstname = None
            self.lastname = None
            self.userid = None

    def setUp(self):
        self.user = self.MockUser()
        self.ogds_user = _PloneUser(self.user)
        self.actor = UserActor('hp.meier', user=self.ogds_user)

    def test_user_label_firstname_and_lastname(self):
        self.user.firstname = 'Hanspeter'
        self.user.lastname = 'Meier'
        self.user.userid = 'hp.meier'

        self.assertEqual('Meier Hanspeter',
                         self.actor.get_label(with_principal=False))

    def test_user_label_lastname(self):
        self.user.lastname = 'Meier'
        self.user.userid = 'hp.meier'

        self.assertEqual('Meier', self.actor.get_label(with_principal=False))

    def test_user_label_firstname(self):
        self.user.firstname = 'Hanspeter'
        self.user.userid = 'hp.meier'

        self.assertEqual('Hanspeter',
                         self.actor.get_label(with_principal=False))

    def test_user_label_id(self):
        self.user.userid = 'hp.meier'

        self.assertEqual('hp.meier',
                          self.actor.get_label(with_principal=False))

    def test_get_label_with_principal(self):
        self.user.firstname = 'Hanspeter'
        self.user.lastname = 'Meier'
        self.user.userid = 'hp.meier'

        self.assertEqual('Meier Hanspeter (hp.meier)',
                         self.actor.get_label())

        self.assertEqual('Meier Hanspeter',
                         self.actor.get_label(with_principal=False))


class TestInboxLabel(TestCase):

    class MockOrgUnit(object):

        def label(self):
            return 'Poscht isch da'

    def setUp(self):
        self.org_unit = self.MockOrgUnit()
        self.actor = InboxActor('some_inbox', org_unit=self.org_unit)

    def test_get_label(self):
        self.assertEqual(u'Inbox: Poscht isch da', self.actor.get_label())
