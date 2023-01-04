from opengever.base.model import create_session
from opengever.contact.models import Address
from opengever.contact.models import ArchivedAddress
from opengever.contact.models import ArchivedMailAddress
from opengever.contact.models import ArchivedPerson
from opengever.contact.models import ArchivedPhoneNumber
from opengever.contact.models import MailAddress
from opengever.contact.models import Person
from opengever.contact.models import PhoneNumber
from opengever.ogds.models.user import User
from pkg_resources import resource_filename
import json
import random


ADDRESS_LABELS = ['Arbeit', 'Privat', None]
PHONENUMBER_LABELS = ['Arbeit', 'Privat', 'Mobile']
ORG_ROLE_FUNCTIONS = [
    None, 'Verwalter', 'Vorsitz', 'Putzfachmann', 'Beratung', 'Angestellter']
COUNTRIES = [u'Schweiz', u'Deutschland', u'\xd6sterreich', u'Belgien']
DEPARTMENTS = [
    None,
    u'ausw\xe4rtige Angelegenheiten',
    u'des Innern',
    u'Justiz- und Polizeidepartement',
    u'Finanzdepartement',
    u'Wirtschaft, Bildung und Forschung',
    u'Umwelt, Verkehr, Energie und Kommunikation'
]


class ContactExampleContentCreator(object):

    def __init__(self):
        self.db_session = create_session()
        self.userids = [
            each[0] for each in self.db_session.query(User.userid).all()]

    @property
    def random_range(self):
        return range(random.choice([0, 0, 0, 1, 2, 3]))

    @property
    def random_actor(self):
        return random.choice(self.userids)

    def load_persons(self):
        path = resource_filename(
            'opengever.examplecontent', 'data/persons.json')
        return json.load(open(path, 'r'))

    def create(self):
        self.create_contacts()

    def create_contacts(self):
        items = self.load_persons()
        for item in items:

            person = Person(salutation=item['salutation'],
                            firstname=item['firstname'],
                            lastname=item['lastname'])
            self.db_session.add(person)
            self.add_archived_persons(person, items)

            self.add_address(item, person, ADDRESS_LABELS)
            self.add_archived_addresses(items, person, ADDRESS_LABELS)
            self.add_phonenumber(item, person, PHONENUMBER_LABELS)
            self.add_archived_phonenumbers(items, person, PHONENUMBER_LABELS)
            self.add_mail(item, person, ADDRESS_LABELS)
            self.add_archived_mails(items, person, ADDRESS_LABELS)

    def add_archived_persons(self, person, items):
        for archive_entry in self.random_range:
            # used to randomly choose a different lastname
            item = random.choice(items)

            archived_person = ArchivedPerson(
                contact=person,
                actor_id=self.random_actor,
                salutation=person.salutation,
                firstname=person.firstname,
                lastname=item['lastname'])
            self.db_session.add(archived_person)

    def add_address(self, item, contact, labels):
        address = Address(label=random.choice(labels),
                          street=item['street'],
                          zip_code=item['zip_code'],
                          city=item['city'],
                          country=random.choice(COUNTRIES),
                          contact=contact)
        self.db_session.add(address)

    def add_archived_addresses(self, items, contact, labels):
        for archive_entry in self.random_range:
            # used to randomly choose a different address
            item = random.choice(items)

            archived_address = ArchivedAddress(
                actor_id=self.random_actor,
                label=random.choice(labels),
                street=item['street'],
                zip_code=item['zip_code'],
                city=item['city'],
                country=random.choice(COUNTRIES),
                contact=contact)
            self.db_session.add(archived_address)

    def add_phonenumber(self, item, contact, labels):
        phonenumber = PhoneNumber(label=random.choice(labels),
                                  phone_number=item['phonenumber'],
                                  contact=contact)
        self.db_session.add(phonenumber)

    def add_archived_phonenumbers(self, items, contact, labels):
        for archive_entry in self.random_range:
            # used to randomly choose a different phonenumber
            item = random.choice(items)

            archived_phonenumber = ArchivedPhoneNumber(
                actor_id=self.random_actor,
                label=random.choice(labels),
                phone_number=item['phonenumber'],
                contact=contact)
            self.db_session.add(archived_phonenumber)

    def add_mail(self, item, contact, labels):
        mail = MailAddress(label=random.choice(labels),
                           address=item['mail'],
                           contact=contact)
        self.db_session.add(mail)

    def add_archived_mails(self, items, contact, labels):
        for archive_entry in self.random_range:
            # used to randomly choose a different mail-address
            item = random.choice(items)

            archived_mail = ArchivedMailAddress(
                actor_id=self.random_actor,
                label=random.choice(labels),
                address=item['mail'],
                contact=contact)
            self.db_session.add(archived_mail)
