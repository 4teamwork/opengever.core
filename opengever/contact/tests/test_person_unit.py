from opengever.contact.models import Address
from opengever.contact.models import Contact
from opengever.contact.models import MailAddress
from opengever.contact.models import Person
from opengever.contact.models import PhoneNumber
from opengever.testing import MEMORY_DB_LAYER
import unittest2


class TestPerson(unittest2.TestCase):

    layer = MEMORY_DB_LAYER

    def test_adding(self):
        Person(firstname=u'Peter',
               lastname='M\xc3\xbcller'.decode('utf-8'))

    def test_is_contact(self):
        person = Person(firstname=u'Peter',
                        lastname='M\xc3\xbcller'.decode('utf-8'))

        self.assertTrue(isinstance(person, Contact))
        self.assertEquals('person', person.contact_type)

    def test_person_can_have_multiple_addresses(self):
        peter = Person(firstname=u'Peter',
                       lastname='M\xc3\xbcller'.decode('utf-8'))

        address1 = Address(contact=peter, label=u'Work',
                           street=u'Dammweg 9', zip_code=u'3013', city=u'Bern')
        address2 = Address(contact=peter, label=u'Home',
                           street=u'Musterstrasse 283', zip_code=u'1700',
                           city=u'Fribourg')

        self.assertEquals([address1, address2], peter.addresses)

    def test_person_can_have_multiple_mail_addresses(self):
        peter = Person(firstname=u'Peter',
                       lastname='M\xc3\xbcller'.decode('utf-8'))

        home = MailAddress(contact=peter, label=u'Work',
                           address=u'peter@example.com')
        work = MailAddress(contact=peter, label=u'Home',
                           address=u'm.peter@example.com')

        self.assertEquals([home, work], peter.mail_addresses)
        self.assertEquals([u'peter@example.com', u'm.peter@example.com'],
                          [mail.address for mail in peter.mail_addresses])

    def test_person_can_have_multiple_phonenumbers(self):
        peter = Person(firstname=u'Peter',
                       lastname='M\xc3\xbcller'.decode('utf-8'))

        home = PhoneNumber(contact=peter, label=u'Work',
                           phone_number=u'+41791234566')
        work = PhoneNumber(contact=peter, phone_number=u'0315110000')

        self.assertEquals([home, work], peter.phonenumbers)
        self.assertEquals([u'+41791234566', u'0315110000'],
                          [phone.phone_number for phone in peter.phonenumbers])

    def test_fullname_is_firstname_and_lastname_separated_with_a_space(self):
        peter = Person(firstname=u'Peter', lastname=u'M\xfcller')
        self.assertEquals(u'Peter M\xfcller', peter.fullname)

    def test_title_is_fullname(self):
        peter = Person(firstname=u'Peter', lastname=u'M\xfcller')
        self.assertEquals(u'Peter M\xfcller', peter.get_title())
