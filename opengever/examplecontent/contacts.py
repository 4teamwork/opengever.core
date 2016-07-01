from opengever.base.model import create_session
from opengever.contact.models import Address
from opengever.contact.models import MailAddress
from opengever.contact.models import Organization
from opengever.contact.models import OrgRole
from opengever.contact.models import Person
from opengever.contact.models import PhoneNumber
from pkg_resources import resource_filename
import json
import random


ADDRESS_LABELS = ['Arbeit', 'Privat', None]
PHONENUMBER_LABELS = ['Arbeit', 'Privat', 'Mobile']


class ExampleContactCreator(object):

    def __init__(self):
        self.db_session = create_session()

    def load_persons(self):
        path = resource_filename(
            'opengever.examplecontent', 'data/persons.json')
        return json.load(open(path, 'r'))

    def load_organizations(self):
        path = resource_filename(
            'opengever.examplecontent', 'data/organizations.json')
        return json.load(open(path, 'r'))

    def create(self):
        organizations = self.create_organizations()
        self.create_contacts(organizations)

    def create_organizations(self):
        organizations = []
        items = self.load_organizations()
        for item in items:
            organization = Organization(name=item['name'])
            self.db_session.add(organization)
            organizations.append(organization)

            self.add_address(item, organization, ['Hauptsitz', None])
            self.add_mail(item, organization, ['Info', 'Support', None])

        return organizations

    def create_contacts(self, organizations=[]):
        items = self.load_persons()
        for item in items:

            person = Person(salutation=item['salutation'],
                            firstname=item['firstname'],
                            lastname=item['lastname'])
            self.db_session.add(person)

            self.add_address(item, person, ADDRESS_LABELS)
            self.add_phonenumber(item, person, PHONENUMBER_LABELS)
            self.add_mail(item, person, ADDRESS_LABELS)

            org_role = OrgRole(person=person,
                               organization=random.choice(organizations))
            self.db_session.add(org_role)

    def add_address(self, item, contact, labels):
        address = Address(label=random.choice(labels),
                          street=item['street'],
                          zip_code=item['zip_code'],
                          city=item['city'],
                          contact=contact)
        self.db_session.add(address)

    def add_phonenumber(self, item, contact, labels):
        phonenumber = PhoneNumber(label=random.choice(labels),
                                  phone_number=item['phonenumber'],
                                  contact=contact)
        self.db_session.add(phonenumber)

    def add_mail(self, item, contact, labels):
        mail = MailAddress(label=random.choice(labels),
                           address=item['mail'],
                           contact=contact)
        self.db_session.add(mail)
