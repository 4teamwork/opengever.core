from opengever.base.model import create_session
from opengever.contact.models import Organization
from opengever.contact.models import Person
from opengever.contact.syncer.object_syncer import AddressSyncer
from opengever.contact.syncer.object_syncer import MailSyncer
from opengever.contact.syncer.object_syncer import OrganizationSyncer
from opengever.contact.syncer.object_syncer import OrgRoleSyncer
from opengever.contact.syncer.object_syncer import PersonSyncer
from opengever.contact.syncer.object_syncer import PhoneNumberSyncer
from opengever.contact.syncer.object_syncer import UrlSyncer
from opengever.testing import FunctionalTestCase
from path import Path
import os


assets = Path('{}/assets/object_syncer/'.format(os.path.dirname(__file__)))


def get_file(name):
    return open(assets.joinpath(name))


class SyncerBaseTest(FunctionalTestCase):

    def setUp(self):
        super(SyncerBaseTest, self).setUp()
        self.session = create_session()

    def tearDown(self):
        super(SyncerBaseTest, self).tearDown()
        self.session.close()


class TestPersonSyncer(SyncerBaseTest):

    def test_add_objects_properly_while_syncing(self):
        syncer = PersonSyncer(get_file('person.csv'))
        syncer()

        self.assertEqual(3, len(Person.query.all()))

        person = Person.query.get_by_former_contact_id(2)

        self.assertItemsEqual(
            [2, u'Frau', u'Dr', u'Christiane', u'W\xfcrsd\xf6rfer'],
            [
                person.former_contact_id,
                person.salutation,
                person.academic_title,
                person.firstname,
                person.lastname,
            ]
            )

    def test_update_object_properly_while_syncing(self):
        syncer = PersonSyncer(get_file('person.csv'))

        self.session.add(Person(
            former_contact_id=2, firstname="james", lastname="bond"))

        person = Person.query.get_by_former_contact_id(2)

        self.assertItemsEqual(
            [2, 'james', 'bond'],
            [
                person.former_contact_id,
                person.firstname,
                person.lastname,
            ]
            )

        syncer()

        self.assertEqual(3, len(Person.query.all()))

        person = Person.query.get_by_former_contact_id(2)

        self.assertItemsEqual(
            [2, u'Christiane', u'W\xfcrsd\xf6rfer'],
            [
                person.former_contact_id,
                person.firstname,
                person.lastname,
            ]
            )


class TestOrganizationSyncer(SyncerBaseTest):

    def setUp(self):
        super(TestOrganizationSyncer, self).setUp()
        self.session = create_session()

    def test_add_objects_properly_while_syncing(self):
        syncer = OrganizationSyncer(get_file('organization.csv'))
        syncer()

        self.assertEqual(2, len(Organization.query.all()))

        organization = Organization.query.get_by_former_contact_id(2)

        self.assertItemsEqual(
            [2, u'Poliz\xe4iwache'],
            [
                organization.former_contact_id,
                organization.name,
            ]
            )

    def test_update_object_properly_while_syncing(self):
        syncer = OrganizationSyncer(get_file('organization.csv'))

        self.session.add(Organization(former_contact_id=2, name="CIA"))

        organization = Organization.query.get_by_former_contact_id(2)

        self.assertItemsEqual(
            [2, 'CIA'],
            [
                organization.former_contact_id,
                organization.name,
            ]
            )

        syncer()

        self.assertEqual(2, len(Organization.query.all()))

        organization = Organization.query.get_by_former_contact_id(2)

        self.assertItemsEqual(
            [2, u'Poliz\xe4iwache'],
            [
                organization.former_contact_id,
                organization.name,
            ]
            )


class TestMailSyncer(SyncerBaseTest):

    def setUp(self):
        super(TestMailSyncer, self).setUp()
        self.session = create_session()

    def test_add_objects_properly_while_syncing(self):
        syncer = MailSyncer(get_file('mail.csv'))

        self.session.add(Person(
            former_contact_id=3, firstname="james", lastname="bond"))

        syncer()

        person = Person.query.get_by_former_contact_id(3)
        mail_addresses = person.mail_addresses

        self.assertEqual(2, len(mail_addresses))

        mail = mail_addresses[0]

        self.assertItemsEqual(
            [1, u'james.bond@test.ch', u'E-Mail'],
            [
                mail.contact_id,
                mail.address,
                mail.label,
            ]
            )


class TestUrlSyncer(FunctionalTestCase):

    def setUp(self):
        super(TestUrlSyncer, self).setUp()
        self.session = create_session()

    def test_add_objects_properly_while_syncing(self):
        syncer = UrlSyncer(get_file('url.csv'))

        self.session.add(Person(
            former_contact_id=3, firstname="james", lastname="bond"))

        syncer()

        person = Person.query.get_by_former_contact_id(3)
        urls = person.urls

        self.assertEqual(2, len(urls))

        url = urls[0]

        self.assertItemsEqual(
            [1, u'www.chuck.ch', u'Web'],
            [
                url.contact_id,
                url.url,
                url.label,
            ]
            )


class TestPhoneNumberSyncer(FunctionalTestCase):

    def setUp(self):
        super(TestPhoneNumberSyncer, self).setUp()
        self.session = create_session()

    def test_add_objects_properly_while_syncing(self):
        syncer = PhoneNumberSyncer(get_file('phonenumber.csv'))

        self.session.add(Person(
            former_contact_id=3, firstname="james", lastname="bond"))

        syncer()

        person = Person.query.get_by_former_contact_id(3)
        phonenumbers = person.phonenumbers

        self.assertEqual(2, len(phonenumbers))

        phonenumber = phonenumbers[0]

        self.assertItemsEqual(
            [1, u'079 111 11 11', u'Telefon'],
            [
                phonenumber.contact_id,
                phonenumber.phone_number,
                phonenumber.label,
            ]
            )


class TestAddressSyncer(FunctionalTestCase):

    def setUp(self):
        super(TestAddressSyncer, self).setUp()
        self.session = create_session()

    def test_add_objects_properly_while_syncing(self):
        syncer = AddressSyncer(get_file('address.csv'))

        self.session.add(Person(
            former_contact_id=3, firstname="james", lastname="bond"))

        syncer()

        person = Person.query.get_by_former_contact_id(3)
        addresses = person.addresses

        self.assertEqual(2, len(addresses))

        address = addresses[0]

        self.assertItemsEqual(
            [1, u"Teststrasse 1", u"1111", u"Bern", u'Gesch\xe4ftsadr.'],
            [
                address.contact_id,
                address.street,
                address.zip_code,
                address.city,
                address.label,
            ]
            )


class TestOrgRoleSyncer(FunctionalTestCase):

    def setUp(self):
        super(TestOrgRoleSyncer, self).setUp()
        self.session = create_session()

    def test_add_objects_properly_while_syncing(self):
        syncer = OrgRoleSyncer(get_file('orgrole.csv'))

        self.session.add(Person(
            former_contact_id=3, firstname="james", lastname="bond"))

        self.session.add(Organization(former_contact_id=2, name="CIA"))

        syncer()

        person = Person.query.get_by_former_contact_id(3)

        orgroles = person.organizations
        self.assertEqual(2, len(orgroles))

        orgrole = orgroles[0]

        self.assertEqual(u'F\xfchrer', orgrole.function)
