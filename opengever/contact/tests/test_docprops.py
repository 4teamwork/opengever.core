from ftw.builder import Builder
from ftw.builder import create
from opengever.contact.ogdsuser import OgdsUserToContactAdapter
from opengever.dossier.tests import OGDS_USER_ATTRIBUTES
from opengever.testing import FunctionalTestCase


class TestContactDocPropertyProvider(FunctionalTestCase):

    use_default_fixture = False
    maxDiff = None

    def setUp(self):
        super(TestContactDocPropertyProvider, self).setUp()

        self.user, org_unit, admin_unit = create(
            Builder('fixture')
            .with_all_unit_setup()
            .with_user(**OGDS_USER_ATTRIBUTES))

        self.set_docproperty_export_enabled(True)

    def tearDown(self):
        self.set_docproperty_export_enabled(False)
        super(TestContactDocPropertyProvider, self).tearDown()

    def test_person_doc_property_provider(self):
        peter = create(Builder('person')
                       .having(firstname=u'Peter',
                               lastname=u'M\xfcller',
                               salutation='Herr',
                               academic_title='Prof. Dr.',
                               description='blablabla'))
        provider = peter.get_doc_property_provider(prefix='recipient')
        expected_person_properties = {
            'ogg.recipient.contact.title': u'M\xfcller Peter',
            'ogg.recipient.contact.description': 'blablabla',
            'ogg.recipient.person.salutation': 'Herr',
            'ogg.recipient.person.academic_title': 'Prof. Dr.',
            'ogg.recipient.person.firstname': 'Peter',
            'ogg.recipient.person.lastname': u'M\xfcller',
        }
        self.assertItemsEqual(expected_person_properties,
                              provider.get_properties())

    def test_organization_doc_property_provider(self):
        organization = create(Builder('organization')
                              .having(name=u'ACME corp.',
                                      description='blablabla'))
        provider = organization.get_doc_property_provider(prefix='recipient')
        expected_organization_properties = {
            'ogg.recipient.contact.title': u'ACME corp.',
            'ogg.recipient.contact.description': 'blablabla',
            'ogg.recipient.organization.name': u'ACME corp.',
        }
        self.assertItemsEqual(expected_organization_properties,
                              provider.get_properties())

    def test_org_role_doc_property_provider(self):
        peter = create(Builder('person')
                       .having(firstname=u'Peter',
                               lastname=u'M\xfcller',
                               salutation='Herr',
                               academic_title='Prof. Dr.',
                               description='blablabla'))
        organization = create(Builder('organization').having(name=u'Foo'))
        org_role = create(Builder('org_role')
                          .having(organization=organization,
                                  person=peter,
                                  function=u'M\xe4dchen f\xfcr alles',
                                  description=u'blub',
                                  department=u'Informatik'))
        provider = org_role.get_doc_property_provider(prefix='recipient')
        expected_orgrole_properties = {
            'ogg.recipient.orgrole.function': u'M\xe4dchen f\xfcr alles',
            'ogg.recipient.orgrole.description': 'blub',
            'ogg.recipient.orgrole.department': 'Informatik',
            'ogg.recipient.contact.title': u'M\xfcller Peter',
            'ogg.recipient.contact.description': 'blablabla',
            'ogg.recipient.person.salutation': 'Herr',
            'ogg.recipient.person.academic_title': 'Prof. Dr.',
            'ogg.recipient.person.firstname': 'Peter',
            'ogg.recipient.person.lastname': u'M\xfcller',
        }
        self.assertItemsEqual(expected_orgrole_properties,
                              provider.get_properties())

    def test_ogds_user_adapter_doc_property_provider(self):
        provider = OgdsUserToContactAdapter(self.user).get_doc_property_provider(
            prefix='recipient')

        expected_ogds_user_properties = {
            'ogg.recipient.contact.title': u'M\xfcller Peter',
            'ogg.recipient.contact.description': u'nix',
            'ogg.recipient.person.salutation': 'Prof. Dr.',
            'ogg.recipient.person.academic_title': '',
            'ogg.recipient.person.firstname': 'Peter',
            'ogg.recipient.person.lastname': u'M\xfcller',
        }
        self.assertItemsEqual(expected_ogds_user_properties,
                              provider.get_properties())

    def test_contact_address_doc_property_provider(self):
        peter = create(Builder('person')
                       .having(firstname=u'Peter',
                               lastname=u'M\xfcller'))
        address = create(Builder('address')
                         .for_contact(peter)
                         .labeled(u'Home')
                         .having(street=u'Musterstrasse 283',
                                 zip_code=u'1234',
                                 city=u'Hinterkappelen',
                                 country=u'Schweiz'))

        provider = address.get_doc_property_provider(prefix='recipient')
        expected_address_properties = {
            'ogg.recipient.address.street': u'Musterstrasse 283',
            'ogg.recipient.address.zip_code': '1234',
            'ogg.recipient.address.city': 'Hinterkappelen',
            'ogg.recipient.address.country': 'Schweiz',
        }
        self.assertItemsEqual(expected_address_properties,
                              provider.get_properties())

    def test_org_role_address_doc_propety_provider(self):
        peter = create(Builder('person')
                       .having(firstname=u'Peter',
                               lastname=u'M\xfcller',
                               salutation='Herr',
                               academic_title='Prof. Dr.',
                               description='blablabla'))
        organization = create(Builder('organization').having(name=u'Foo'))
        create(Builder('address')
               .for_contact(organization)
               .labeled(u'Main')
               .having(street=u'Musterstrasse 1234',
                       zip_code=u'7335',
                       city=u'Obermumpf',
                       country=u'Schweiz'))
        org_role = create(Builder('org_role')
                          .having(organization=organization,
                                  person=peter,
                                  function=u'M\xe4dchen f\xfcr alles',
                                  description=u'blub',
                                  department=u'Informatik'))

        org_role_address = org_role.addresses[0]
        provider = org_role_address.get_doc_property_provider(
            prefix='recipient')
        expected_address_properties = {
            'ogg.recipient.organization.name': u'Foo',
            'ogg.recipient.address.street': u'Musterstrasse 1234',
            'ogg.recipient.address.zip_code': '7335',
            'ogg.recipient.address.city': 'Obermumpf',
            'ogg.recipient.address.country': 'Schweiz',
        }
        self.assertItemsEqual(expected_address_properties,
                              provider.get_properties())

    def test_contact_mail_address_doc_property_provider(self):
        peter = create(Builder('person')
                       .having(firstname=u'Peter',
                               lastname=u'M\xfcller'))
        mail_address = create(Builder('mailaddress')
                              .for_contact(peter)
                              .labeled(u'Private')
                              .having(address=u'peter@example.com'))

        provider = mail_address.get_doc_property_provider(prefix='recipient')
        expected_address_properties = {
            'ogg.recipient.email.address': u'peter@example.com',
        }
        self.assertItemsEqual(expected_address_properties,
                              provider.get_properties())

    def test_contact_phonenumber_doc_property_provider(self):
        peter = create(Builder('person')
                       .having(firstname=u'Peter',
                               lastname=u'M\xfcller'))
        phonenumber = create(Builder('phonenumber')
                             .for_contact(peter)
                             .labeled(u'Psst')
                             .having(phone_number=u'0190 666 666'))

        provider = phonenumber.get_doc_property_provider(prefix='recipient')
        expected_phone_properties = {
            'ogg.recipient.phone.number': u'0190 666 666',
        }
        self.assertItemsEqual(expected_phone_properties,
                              provider.get_properties())

    def test_contact_url_doc_property_provider(self):
        peter = create(Builder('person')
                       .having(firstname=u'Peter',
                               lastname=u'M\xfcller'))
        url = create(Builder('url')
                     .for_contact(peter)
                     .labeled(u'There')
                     .having(url=u'http://www.example.com'))

        provider = url.get_doc_property_provider(prefix='recipient')
        expected_url_properties = {
            'ogg.recipient.url.url': u'http://www.example.com',
        }
        self.assertItemsEqual(expected_url_properties,
                              provider.get_properties())
