from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.contact.browser.related_entity import IRelatedEntityCRUDActions
from opengever.contact.browser.phonenumbers import PhoneNumbersView
from opengever.contact.models import PhoneNumber
from opengever.testing import FunctionalTestCase
from zExceptions import NotFound
from zope.interface.verify import verifyClass


class TestPhoneNumbersView(FunctionalTestCase):

    def setUp(self):
        super(TestPhoneNumbersView, self).setUp()
        self.contactfolder = create(Builder('contactfolder'))
        self.contact = create(Builder('person')
                              .having(firstname=u'Peter',
                                      lastname=u'M\xfcller'))

    def test_verify_interface(self):
        self.assertTrue(
            verifyClass(IRelatedEntityCRUDActions, PhoneNumbersView))

    @browsing
    def test_add_phonenumber(self, browser):
        browser.login().visit(
            self.contactfolder,
            {'label': 'Private', 'phone_number': '099 313 51 95'},
            view='person-1/phonenumbers/add')

        phonenumber = PhoneNumber.query.first()

        self.assertEqual('Private', phonenumber.label)
        self.assertEqual('099 313 51 95', phonenumber.phone_number)

        self.assertDictContainsSubset({
            'message': 'The object was added successfully',
            'messageClass': 'info'},
            browser.json.get('messages')[0])

        self.assertDictContainsSubset({u'proceed': True}, browser.json)

    @browsing
    def test_add_phonenumber_without_number_returns_validation_error(self, browser):
        browser.login().visit(
            self.contactfolder,
            {'label': 'Private'},
            view='person-1/phonenumbers/add')

        self.assertEquals(0, PhoneNumber.query.count())

        self.assertDictContainsSubset({
            'message': 'Please specify an phone number',
            'messageClass': 'error'},
            browser.json.get('messages')[0])

    @browsing
    def test_lists_multiple_phonenumbers(self, browser):
        create(Builder('phonenumber')
               .for_contact(self.contact)
               .having(
                   label=u'Private',
                   phone_number=u"099 313 51 95"))

        create(Builder('phonenumber')
               .for_contact(self.contact)
               .having(
                   label=u'Business',
                   phone_number=u"099 313 11 11"))

        browser.login().visit(self.contactfolder,
                              view='person-1/phonenumbers/list')


        item1, item2 = browser.json.get('objects')
        self.assertDictContainsSubset(
            {u'phone_number': u'099 313 51 95',
             u'label': u'Private',
             u'contact_id': 1,
             u'id': 1},
            item1)
        self.assertDictContainsSubset(
            {u'phone_number': u'099 313 11 11',
             u'label': u'Business',
             u'contact_id': 1,
             u'id': 2},
            item2)

    @browsing
    def test_lists_no_phonenumbers(self, browser):
        browser.login().visit(self.contactfolder,
                              view='person-1/phonenumbers/list')

        self.assertEqual(0, len(browser.json.get('objects')))

    @browsing
    def test_delete_given_phonenumber(self, browser):
        create(Builder('phonenumber').for_contact(self.contact))

        self.assertEqual(1, PhoneNumber.query.count())

        browser.login().visit(self.contactfolder,
                              view='person-1/phonenumbers/1/delete')

        self.assertDictContainsSubset(
            {'message': 'Object successfully deleted',
             'messageClass': 'info'},
            browser.json.get('messages')[0])

        self.assertEqual(0, PhoneNumber.query.count())

    @browsing
    def test_update_label_and_address_of_existing_phonenumber(self, browser):
        create(Builder('phonenumber')
               .for_contact(self.contact)
               .having(
                   label=u'Private',
                   phone_number=u"099 333 11 22"))

        browser.login().visit(
            self.contactfolder,
            {'label': 'Business', 'phone_number': '099 333 44 55'},
            view='person-1/phonenumbers/1/update')

        phonenumber = PhoneNumber.query.first()

        self.assertEqual('Business', phonenumber.label)
        self.assertEqual('099 333 44 55', phonenumber.phone_number)

        self.assertDictContainsSubset(
            {'message': 'Object updated.', 'messageClass': 'info'},
            browser.json.get('messages')[0])

    @browsing
    def test_raise_not_found_if_not_api_function_or_id_is_called(self, browser):
        with self.assertRaises(NotFound):
            browser.login().visit(self.contactfolder,
                                  view='person-1/phonenumbers/bad_name')

    @browsing
    def test_raise_not_found_if_no_phonenumber_with_the_given_id_exists(self, browser):
        with self.assertRaises(NotFound):
            browser.login().visit(self.contactfolder, view='person-1/mails/10')

    @browsing
    def test_raise_not_found_if_phonenumber_is_not_linked_to_the_given_context(self, browser):
        other_contact = create(Builder('person')
                               .having(firstname=u'Peter',
                                       lastname=u'M\xfcller'))
        phonenumber = create(Builder('phonenumber')
                             .for_contact(other_contact)
                             .labeled(u'Home')
                             .having(phone_number=u'099 887 77 88'))

        with self.assertRaises(NotFound):
            browser.login().visit(
                self.contactfolder,
                view='person-1/phonenumbers/{}'.format(
                    phonenumber.phone_number_id))
