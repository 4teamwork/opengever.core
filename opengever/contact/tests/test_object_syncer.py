from ftw.builder import Builder
from ftw.builder import create
from opengever.base.model import create_session
from opengever.contact.models import Organization
from opengever.contact.models import OrgRole
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
from pkg_resources import resource_string
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.orm import sessionmaker
import os
import transaction


assets = Path('{}/assets/object_syncer/'.format(os.path.dirname(__file__)))


def load_asset(name):
    return resource_string('opengever.contact.tests',
                           'assets/object_syncer/{}'.format(name))


class SyncerBaseTest(FunctionalTestCase):

    SAMPLE_DATA = []

    def setUp(self):
        super(SyncerBaseTest, self).setUp()
        self.session = create_session()

        engine = create_engine('sqlite:///:memory:')
        self.source_db = sessionmaker(bind=engine)()
        self.source_metadata = MetaData(engine)
        self.create_source_db()
        self.insert_sample_data()

    def create_source_db(self):
        raise NotImplementedError

    def insert_sample_data(self):
        for item in self.SAMPLE_DATA:
            self.source_db.execute(
                self.source_table.insert().values(**item))

    def tearDown(self):
        super(SyncerBaseTest, self).tearDown()
        self.session.close()


class TestPersonSyncer(SyncerBaseTest):

    SAMPLE_DATA = [{u'is_active': True, u'former_contact_id': 1,
                    u'firstname': u'Frank G.', u'lastname': u'Dippel',
                    u'salutation': u'Herr', u'title': u'Dr.'},
                   {u'is_active': False, u'former_contact_id': 2,
                    u'firstname': u'Christiane',
                    u'lastname': u'W\xfcrsd\xf6rfer',
                    u'salutation': u'Frau', u'title': u'B.Sc.'},
                   {u'is_active': True, u'former_contact_id': 3,
                    u'firstname': u'Dolorene', u'lastname': u'Dolores',
                    u'salutation': u'Frau', u'title': u''}]

    def create_source_db(self):
        self.source_table = Table("persons",
                                  self.source_metadata,
                                  Column("former_contact_id", Integer),
                                  Column("salutation", String),
                                  Column("title", String),
                                  Column("firstname", String),
                                  Column("lastname", String),
                                  Column("is_active", Boolean))
        self.source_table.create()

    def test_add_objects_properly_while_syncing(self):
        syncer = PersonSyncer(self.source_db, 'SELECT * from persons')
        syncer()

        self.assertEqual(3, len(Person.query.all()))

        person = Person.query.get_by_former_contact_id(2)
        self.assertItemsEqual(
            [u'Frau', u'B.Sc.', u'Christiane', u'W\xfcrsd\xf6rfer', False, 2],
            [person.salutation, person.academic_title, person.firstname,
             person.lastname, person.is_active, person.former_contact_id])

        person = Person.query.get_by_former_contact_id(1)
        self.assertItemsEqual(
            [u'Herr', u'Dr.', u'Frank G.', u'Dippel', True],
            [person.salutation, person.academic_title, person.firstname,
             person.lastname, person.is_active])

    def test_update_object_properly_while_syncing(self):
        syncer = PersonSyncer(self.source_db, 'SELECT * from persons')
        syncer()

        self.assertEqual(3, len(Person.query.all()))

        self.source_db.execute(
            self.source_table.update().where(
                self.source_table.c.former_contact_id == 3).values(
                    lastname=u'Meier', is_active=False))

        PersonSyncer(self.source_db, 'SELECT * from persons')()

        self.assertEqual(3, len(Person.query.all()))
        person = Person.query.get_by_former_contact_id(3)
        self.assertEquals('Meier', person.lastname)
        self.assertFalse(person.is_active)


class TestOrganizationSyncer(SyncerBaseTest):

    SAMPLE_DATA = [{u'is_active': True,
                    u'former_contact_id': 2344,
                    u'name': u'Soziale Dienste'},
                   {u'is_active': False,
                    u'former_contact_id': 5637,
                    u'name': u'Poliz\xe4iwache'}]

    def create_source_db(self):
        self.source_table = Table("organizations",
                                  self.source_metadata,
                                  Column("former_contact_id", Integer),
                                  Column("name", String),
                                  Column("is_active", Boolean))
        self.source_table.create()

    def test_add_objects_properly_while_syncing(self):
        OrganizationSyncer(self.source_db, 'SELECT * from organizations')()

        self.assertEqual(2, len(Organization.query.all()))

        organizations = Organization.query.all()
        self.assertEqual(
            [u'Soziale Dienste', u'Poliz\xe4iwache'],
            [org.name for org in organizations])
        self.assertEqual(
            [2344, 5637],
            [org.former_contact_id for org in organizations])

    def test_update_existing_objects_properly_while_syncing(self):
        OrganizationSyncer(self.source_db, 'SELECT * from organizations')()
        transaction.commit()
        self.assertEqual(2, len(Organization.query.all()))

        self.source_db.execute(
            self.source_table.update().where(
                self.source_table.c.former_contact_id == 5637).values(
                    name=u'CIA', is_active=True))

        OrganizationSyncer(self.source_db, 'SELECT * from organizations')()
        transaction.commit()

        self.assertEqual(2, len(Organization.query.all()))

        organization = Organization.query.get_by_former_contact_id(5637)
        self.assertEquals('CIA', organization.name)
        self.assertTrue(organization.is_active)


class TestMailSyncer(SyncerBaseTest):

    SAMPLE_DATA = [{u'former_contact_id': 2344,
                    u'address': u'foo@example.com',
                    u'label': u'E-Mail (gesch\xe4ftlich)'},
                   {u'former_contact_id': 2344,
                    u'address': u'bar@example.com',
                    u'label': u'E-Mail (privat)'}]

    def create_source_db(self):
        self.source_table = Table("mails",
                                  self.source_metadata,
                                  Column("former_contact_id", Integer),
                                  Column("address", String),
                                  Column("label", String))
        self.source_table.create()

    def test_add_mails_properly_while_syncing(self):
        organization = create(Builder('organization')
                              .having(name=u'Meier AG',
                                      former_contact_id=2344))

        MailSyncer(self.source_db, 'SELECT * from mails')()
        transaction.commit()

        organization = Organization.query.first()
        self.assertEquals(2, len(organization.mail_addresses))
        self.assertEquals(
            [u'E-Mail (gesch\xe4ftlich)', u'E-Mail (privat)'],
            [mail.label for mail in organization.mail_addresses])
        self.assertEquals(
            [u'foo@example.com', u'bar@example.com'],
            [mail.address for mail in organization.mail_addresses])

    def test_updates_existing_mailaddresses_properly_by_label(self):
        org_1 = create(Builder('organization')
                       .having(name=u'Meier AG', former_contact_id=2344))
        org_2 = create(Builder('organization')
                       .having(name=u'James AG', former_contact_id=5555))

        create(Builder('mailaddress')
               .for_contact(org_1)
               .having(label=u'E-Mail (privat)',
                       address=u'private@example.com'))
        create(Builder('mailaddress')
               .for_contact(org_2)
               .having(label=u'E-Mail (gesch\xe4ftlich)',
                       address=u'james@example.com'))

        MailSyncer(self.source_db, 'SELECT * from mails')()
        transaction.commit()

        org_1, org_2 = Organization.query.all()
        self.assertEquals(2, len(org_1.mail_addresses))
        self.assertEquals(1, len(org_2.mail_addresses))

        self.assertEquals(
            [u'E-Mail (privat)', u'E-Mail (gesch\xe4ftlich)'],
            [mail.label for mail in org_1.mail_addresses])
        self.assertEquals(
            [u'bar@example.com', u'foo@example.com'],
            [mail.address for mail in org_1.mail_addresses])


class TestURLSyncer(SyncerBaseTest):

    SAMPLE_DATA = [{u'former_contact_id': 2344,
                    u'url': u'www.shop.example.com',
                    u'label': u'Shop'},
                   {u'former_contact_id': 2344,
                    u'url': u'http://www.website.example.com',
                    u'label': u'Website'},
                   {u'former_contact_id': 30,
                    u'url': u'https://intern.example.com',
                    u'label': u'Intranet'}]

    def setUp(self):
        super(TestURLSyncer, self).setUp()
        self.org1 = create(Builder('organization')
                           .having(name=u'Meier AG',
                                   former_contact_id=2344))
        self.org1 = create(Builder('organization')
                           .having(name=u'Example AG',
                                   former_contact_id=30))

    def create_source_db(self):
        self.source_table = Table("urls",
                                  self.source_metadata,
                                  Column("former_contact_id", Integer),
                                  Column("url", String),
                                  Column("label", String))
        self.source_table.create()

    def test_add_urls_properly_while_syncing(self):
        UrlSyncer(self.source_db, 'SELECT * from urls')()

        org1, org2 = Organization.query.all()
        self.assertEquals(
            [u'Shop', u'Website'], [url.label for url in org1.urls])
        self.assertEquals(
            [u'http://www.shop.example.com',
             u'http://www.website.example.com'],
            [url.url for url in org1.urls])

        self.assertEquals(
            [u'Intranet'], [url.label for url in org2.urls])
        self.assertEquals(
            [u'https://intern.example.com'],
            [url.url for url in org2.urls])

    def test_updates_existing_urls_properly_by_label(self):
        create(Builder('url')
               .for_contact(self.org1)
               .having(label=u'Shop',
                       url=u'http://www.old_shop.example.com'))

        UrlSyncer(self.source_db, 'SELECT * from urls')()

        org1, org2 = Organization.query.all()
        self.assertEquals(
            [u'Shop', u'Website'], [url.label for url in org1.urls])
        self.assertEquals(
            [u'http://www.shop.example.com',
             u'http://www.website.example.com'],
            [url.url for url in org1.urls])


class TestPhoneNumberSyncer(SyncerBaseTest):

    SAMPLE_DATA = [{u'former_contact_id': 2344,
                    u'phone_number': u'099 11 22 33',
                    u'label': u'Gesch\xe4ftlich'},
                   {u'former_contact_id': 2344,
                    u'phone_number': u'099 22 33 44',
                    u'label': u'Privat'}]

    def create_source_db(self):
        self.source_table = Table("phonenumbers",
                                  self.source_metadata,
                                  Column("former_contact_id", Integer),
                                  Column("phone_number", String),
                                  Column("label", String))
        self.source_table.create()

    def test_add_phonenumbers_properly_while_syncing(self):
        organization = create(Builder('organization')
                              .having(name=u'Meier AG',
                                      former_contact_id=2344))

        PhoneNumberSyncer(self.source_db, 'SELECT * from phonenumbers')()

        organization = Organization.query.first()
        self.assertEquals(2, len(organization.phonenumbers))
        self.assertEquals(
            [u'Gesch\xe4ftlich', u'Privat'],
            [phone.label for phone in organization.phonenumbers])
        self.assertEquals(
            [u'099 11 22 33', u'099 22 33 44'],
            [phone.phone_number for phone in organization.phonenumbers])

    def test_updates_existing_phonenumbers_properly_by_label(self):
        organization = create(Builder('organization')
                              .having(name=u'Meier AG',
                                      former_contact_id=2344))
        create(Builder('phonenumber')
               .for_contact(organization)
               .having(label=u'Privat',
                       phone_number=u'099 33 44 55'))

        PhoneNumberSyncer(self.source_db, 'SELECT * from phonenumbers')()

        organization = Organization.query.first()
        self.assertEquals(2, len(organization.phonenumbers))
        self.assertEquals(
            [u'Privat', u'Gesch\xe4ftlich'],
            [phone.label for phone in organization.phonenumbers])
        self.assertEquals(
            [u'099 22 33 44', u'099 11 22 33'],
            [phone.phone_number for phone in organization.phonenumbers])


class TestAddressSyncer(SyncerBaseTest):

    SAMPLE_DATA = [{u'former_contact_id': 2344,
                    u'label': u'Hauptsitz',
                    u'street': u'Teststrasse 1',
                    u'zip_code': u'1111',
                    u'city': u'Bern',
                    u'country': u'Schweiz'},
                   {u'former_contact_id': 2344,
                    u'label': u'Standort Romandie',
                    u'street': u'Rue de Lausanne',
                    u'zip_code': u'2222',
                    u'city': u'Fribourg',
                    u'country': u'Schweiz'}]

    def create_source_db(self):
        self.source_table = Table("addresses",
                                  self.source_metadata,
                                  Column("former_contact_id", Integer),
                                  Column("label", String),
                                  Column("street", String),
                                  Column("zip_code", String),
                                  Column("city", String),
                                  Column("country", String))
        self.source_table.create()

    def test_add_addresses_properly_while_syncing(self):
        organization = create(Builder('organization')
                              .having(name=u'Meier AG',
                                      former_contact_id=2344))

        AddressSyncer(self.source_db, 'SELECT * from addresses')()

        organization = Organization.query.first()
        self.assertEquals(2, len(organization.addresses))

        address_1, address_2 = organization.addresses

        self.assertEquals(u'Hauptsitz', address_1.label)
        self.assertEquals(u'Teststrasse 1', address_1.street)
        self.assertEquals(u'1111', address_1.zip_code)
        self.assertEquals(u'Bern', address_1.city)
        self.assertEquals(u'Schweiz', address_1.country)

    def test_updates_addresses_while_syncing(self):
        organization = create(Builder('organization')
                              .having(name=u'Meier AG',
                                      former_contact_id=2344))

        create(Builder('address')
               .for_contact(organization)
               .labeled(u'Hauptsitz')
               .having(street=u'Dammweg 9', zip_code=u'3013', city=u'Bern'))

        AddressSyncer(self.source_db, 'SELECT * from addresses')()
        transaction.commit()

        organization = Organization.query.first()
        self.assertEquals(2, len(organization.addresses))

        self.assertEquals(
            [u'Hauptsitz', u'Standort Romandie'],
            [address.label for address in organization.addresses])
        self.assertEquals(
            [u'Teststrasse 1', u'Rue de Lausanne'],
            [address.street for address in organization.addresses])


class TestOrganizationRoleSyncer(SyncerBaseTest):

    SAMPLE_DATA = [{u'person_id': 1111,
                    u'organization_id': 2222,
                    u'function': u'Leitung'},
                   {u'person_id': 3333,
                    u'organization_id': 2222,
                    u'function': u'Vorsteher'}]

    def create_source_db(self):
        self.source_table = Table("orgroles",
                                  self.source_metadata,
                                  Column("person_id", Integer),
                                  Column("organization_id", Integer),
                                  Column("function", String))
        self.source_table.create()

    def test_add_organization_roles_properly_while_syncing(self):
        create(Builder('organization')
               .having(name=u'Meier AG', former_contact_id=2222))

        create(Builder('person')
               .having(lastname=u'Meier', firstname=u'Peter',
                       former_contact_id=1111))
        create(Builder('person')
               .having(lastname=u'Bond', firstname=u'James',
                       former_contact_id=3333))

        OrgRoleSyncer(self.source_db, 'SELECT * from orgroles')()
        transaction.commit()

        org_roles = Organization.query.first().persons
        self.assertEquals([u'Leitung', u'Vorsteher'],
                          [role.function for role in org_roles])
        self.assertEquals(['Peter', 'James'],
                          [role.person.firstname for role in org_roles])

    def test_update_existing_organization_roles(self):
        org1 = create(Builder('organization')
                      .having(name=u'Meier AG',
                              former_contact_id=2222))
        org2 = create(Builder('organization')
                      .having(name=u'Search AG',
                              former_contact_id=4444))

        peter = create(Builder('person')
                       .having(lastname=u'Meier', firstname=u'Peter',
                               former_contact_id=1111))
        create(Builder('person')
               .having(lastname=u'Bond', firstname=u'James',
                       former_contact_id=3333))

        create(Builder('org_role')
               .having(person=peter, organization=org1,
                       function='Stellv. Leitung'))

        OrgRoleSyncer(self.source_db, 'SELECT * from orgroles')()
        self.assertEquals(2, OrgRole.query.count())
        self.assertEquals([u'Leitung', u'Vorsteher'],
                          [aa.function for aa in OrgRole.query])
