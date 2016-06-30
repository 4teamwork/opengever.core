from opengever.base.model import create_session
from opengever.contact.models import Address
from opengever.contact.models import MailAddress
from opengever.contact.models import Person
from opengever.contact.models import PhoneNumber
from pkg_resources import resource_filename
import json
import random


ADDRESS_LABELS = ['Arbeit', 'Privat', None]
PHONENUMBER_LABELS = ['Arbeit', 'Privat', 'Mobile']


class ExampleContactCreator(object):

    def __init__(self, site):
        self.site = site
        self.db_session = create_session()

    def load_contacts(self):
        path = resource_filename(
            'opengever.examplecontent', 'data/contacts.json')
        _file = open(path, 'r')
        return json.loads(_file.read())

    def create(self):
        items = self.load_contacts()
        for item in items:
            person = Person(academic_title=item['title'],
                            firstname=item['firstname'],
                            lastname=item['lastname'])
            self.db_session.add(person)

            address = Address(label=random.choice(ADDRESS_LABELS),
                              street=item['street'],
                              zip_code=str(item['zip_code']),
                              city=item['city'],
                              contact=person)
            self.db_session.add(address)

            phonenumber = PhoneNumber(label=random.choice(PHONENUMBER_LABELS),
                                      number=item['phonenumber'],
                                      contact=person)
            self.db_session.add(phonenumber)

            mail = MailAddress(label=random.choice(ADDRESS_LABELS),
                               address=item['mail'],
                               contact=person)
            self.db_session.add(mail)
