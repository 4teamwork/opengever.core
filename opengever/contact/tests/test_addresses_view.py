from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.contact.browser.addresses import AddressesView
from opengever.contact.browser.related_entity import IRelatedEntityCRUDActions
from opengever.contact.models import Address
from opengever.testing import FunctionalTestCase
from zope.interface.verify import verifyClass


class TestAddressesView(FunctionalTestCase):

    def setUp(self):
        super(TestAddressesView, self).setUp()
        self.contactfolder = create(Builder('contactfolder'))
        self.contact = create(Builder('person')
                              .having(firstname=u'Peter',
                                      lastname=u'M\xfcller'))

    def test_verify_interface(self):
        self.assertTrue(verifyClass(IRelatedEntityCRUDActions, AddressesView))

    @browsing
    def test_add_address(self, browser):
        browser.login().visit(
            self.contactfolder,
            {'label': 'Private',
             'street': 'Panoramaweg 23',
             'zip_code': '3013',
             'city': 'Bern'},
            view='person-1/addresses/add')

        address = Address.query.first()

        self.assertEqual('Private', address.label)
        self.assertEqual('Panoramaweg 23', address.street)
        self.assertEqual('3013', address.zip_code)
        self.assertEqual('Bern', address.city)

        self.assertDictContainsSubset({u'proceed': True}, browser.json)
        self.assertDictContainsSubset(
            {'message': 'The object was added successfully',
             'messageClass': 'info'},
            browser.json.get('messages')[0])

    @browsing
    def test_lists_multiple_addresses(self, browser):
        create(Builder('address')
               .for_contact(self.contact)
               .having(label=u'Private',
                       street=u'Panoramaweg 23',
                       zip_code=u'3013',
                       city=u'Bern'))
        create(Builder('address')
               .for_contact(self.contact)
               .having(label=u'Work',
                       street=u'Rue de Romont',
                       zip_code=u'1700',
                       city=u'Fribourg'))

        browser.login().visit(self.contactfolder,
                              view='person-1/addresses/list')

        item1, item2 = browser.json.get('objects')
        self.assertDictContainsSubset(
            {u'city': u'Bern',
             u'contact_id': 1,
             u'id': 1,
             u'label': u'Private',
             u'street': u'Panoramaweg 23',
             u'zip_code': u'3013'},
            item1)
        self.assertDictContainsSubset(
            {u'city': u'Fribourg',
             u'contact_id': 1,
             u'id': 2,
             u'label': u'Work',
             u'street': u'Rue de Romont',
             u'zip_code': u'1700'},
            item2)

    @browsing
    def test_delete_existing_address(self, browser):
        create(Builder('address').for_contact(self.contact))

        browser.login().visit(self.contactfolder,
                              view='person-1/addresses/1/delete')

        self.assertDictContainsSubset(
            {'message': 'Object successfully deleted',
             'messageClass': 'info'},
            browser.json.get('messages')[0])

        self.assertEqual(0, Address.query.count())

    @browsing
    def test_update_label_and_address_of_existing_address(self, browser):
        create(Builder('address')
               .for_contact(self.contact)
               .having(label=u'Private',
                       street=u'Panoramaweg 23',
                       zip_code=u'3013',
                       city=u'Bern'))

        browser.login().visit(
            self.contactfolder,
            {'label': 'Business', 'street': u'Rue de Romont',
             'zip_code': u'1700', 'city': u'Fribourg'},
            view='person-1/addresses/1/update')

        address = Address.query.first()
        self.assertEqual(u'Business', address.label)
        self.assertEqual(u'Rue de Romont', address.street)
        self.assertEqual(u'1700', address.zip_code)
        self.assertEqual(u'Fribourg', address.city)

        self.assertDictContainsSubset(
            {'message': 'Object updated.', 'messageClass': 'info'},
            browser.json.get('messages')[0])
