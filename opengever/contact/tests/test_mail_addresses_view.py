from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.model import create_session
from opengever.contact.browser.mail import MailAddressesView
from opengever.contact.browser.related_entity import IRelatedEntityCRUDActions
from opengever.contact.models.mailaddress import MailAddress
from opengever.testing import FunctionalTestCase
from zExceptions import NotFound
from zope.interface.verify import verifyClass


class TestMailAddressesView(FunctionalTestCase):

    def setUp(self):
        super(TestMailAddressesView, self).setUp()
        self.grant('Manager')
        self.session = create_session()

        self.contactfolder = create(Builder('contactfolder'))
        self.contact = create(Builder('person')
                              .having(firstname=u'Peter', lastname=u'M\xfcller'))

    def test_verify_interface(self):
        self.assertTrue(
            verifyClass(IRelatedEntityCRUDActions, MailAddressesView))

    @browsing
    def test_add_mailaddress(self, browser):
        browser.login().visit(
            self.contactfolder,
            {'label': 'Private', 'address': 'max.muster@example.com'},
            view='person-1/mails/add')

        mailaddress = MailAddress.query.first()

        self.assertEqual('Private', mailaddress.label)
        self.assertEqual('max.muster@example.com', mailaddress.address)

        self.assertDictContainsSubset({
            'message': 'The object was added successfully',
            'messageClass': 'info'},
            browser.json.get('messages')[0])

        self.assertDictContainsSubset({u'proceed': True}, browser.json)

    @browsing
    def test_add_mailaddress_without_label(self, browser):
        browser.login().visit(
            self.contactfolder,
            {'address': 'max.muster@example.com'},
            view='person-1/mails/add')

        self.assertEquals(0, self.session.query(MailAddress).count())

        self.assertDictContainsSubset({
            'message': 'Please specify a label for your email address',
            'messageClass': 'error'},
            browser.json.get('messages')[0])

    @browsing
    def test_add_mailaddress_without_address(self, browser):
        browser.login().visit(
            self.contactfolder,
            {'label': 'Private'},
            view='person-1/mails/add')

        self.assertEquals(0, self.session.query(MailAddress).count())

        self.assertDictContainsSubset({
            'message': 'Please specify an email address',
            'messageClass': 'error'},
            browser.json.get('messages')[0])

    @browsing
    def test_add_mailaddress_without_a_valid_address(self, browser):
        browser.login().visit(
            self.contactfolder,
            {'label': 'Private', 'address': 'bademail'},
            view='person-1/mails/add')

        self.assertEquals(0, self.session.query(MailAddress).count())

        self.assertDictContainsSubset({
            'message': 'Please specify a valid email address',
            'messageClass': 'error'},
            browser.json.get('messages')[0])

    @browsing
    def test_add_mailaddress_without_address_and_label(self, browser):
        browser.login().visit(
            self.contactfolder,
            view='person-1/mails/add')

        self.assertEquals(0, self.session.query(MailAddress).count())

        self.assertDictContainsSubset({
            'message': 'Please specify a label and an email address.',
            'messageClass': 'error'},
            browser.json.get('messages')[0])

    @browsing
    def test_list_multiple_mailaddresses(self, browser):
        create(Builder('mailaddress')
               .for_contact(self.contact)
               .having(
                   label=u'Private',
                   address=u"max.muster@example.com"))

        create(Builder('mailaddress')
               .for_contact(self.contact)
               .having(
                   label=u'Business',
                   address=u"max.muster@foo.com"))

        browser.login().visit(self.contactfolder, view='person-1/mails/list')

        item1, item2 = browser.json.get('objects')
        self.assertDictContainsSubset(
            {u'contact_id': 1,
             u'id': 1,
             u'label': u'Private',
             u'address': u'max.muster@example.com'},
            item1)
        self.assertDictContainsSubset(
            {u'contact_id': 1,
             u'id': 2,
             u'label': u'Business',
             u'address': u'max.muster@foo.com'},
            item2)

    @browsing
    def test_list_no_mailaddresses(self, browser):
        browser.login().visit(self.contactfolder, view='person-1/mails/list')

        self.assertEqual(0, len(browser.json.get('objects')))

    @browsing
    def test_delete_given_mailaddress(self, browser):
        create(Builder('mailaddress').for_contact(self.contact))

        self.assertEqual(1, self.session.query(MailAddress).count())

        browser.login().visit(self.contactfolder, view='person-1/mails/1/delete')

        self.assertDictContainsSubset({
            'message': 'Object successfully deleted',
            'messageClass': 'info'},
            browser.json.get('messages')[0])

        self.assertEqual(0, self.session.query(MailAddress).count())

    @browsing
    def test_update_given_mailaddress_label_and_address(self, browser):
        create(Builder('mailaddress')
               .for_contact(self.contact)
               .having(
                   label=u'Private',
                   address=u"max.muster@example.com"))

        self.assertEqual(1, self.session.query(MailAddress).count())

        browser.login().visit(
            self.contactfolder,
            {'label': 'Business', 'address': 'james.bond@example.com'},
            view='person-1/mails/1/update')

        mailaddress = MailAddress.query.first()

        self.assertEqual('Business', mailaddress.label)
        self.assertEqual('james.bond@example.com', mailaddress.address)

        self.assertDictContainsSubset({
            'message': 'Object updated.',
            'messageClass': 'info'},
            browser.json.get('messages')[0])

    @browsing
    def test_update_given_mailaddress_label(self, browser):
        create(Builder('mailaddress')
               .for_contact(self.contact)
               .having(
                   label=u'Private',
                   address=u"max.muster@example.com"))

        browser.login().visit(
            self.contactfolder,
            {'label': 'Business'},
            view='person-1/mails/1/update')

        mailaddress = MailAddress.query.first()

        self.assertEqual('Business', mailaddress.label)
        self.assertEqual('max.muster@example.com', mailaddress.address)

    @browsing
    def test_update_given_mailaddress_address(self, browser):
        create(Builder('mailaddress')
               .for_contact(self.contact)
               .having(
                   label=u'Private',
                   address=u"max.muster@example.com"))

        browser.login().visit(
            self.contactfolder,
            {'address': 'james.bond@example.com'},
            view='person-1/mails/1/update')

        mailaddress = MailAddress.query.first()

        self.assertEqual('Private', mailaddress.label)
        self.assertEqual('james.bond@example.com', mailaddress.address)

    @browsing
    def test_call_api_function_if_available(self, browser):
        browser.login().visit(self.contactfolder, view='person-1/mails/list')

        self.assertEqual(['objects'], browser.json.keys())

    @browsing
    def test_raise_not_found_if_not_an_api_function_and_not_a_number(self, browser):
        with self.assertRaises(NotFound):
            browser.login().visit(self.contactfolder, view='person-1/mails/bad_name')

    @browsing
    def test_raise_not_found_if_mail_address_id_is_already_set_on_view(self, browser):
        with self.assertRaises(NotFound):
            browser.login().visit(self.contactfolder, view='person-1/mails/10/100')

    @browsing
    def test_raise_not_found_if_no_mailaddress_with_the_given_id_exists(self, browser):
        with self.assertRaises(NotFound):
            browser.login().visit(self.contactfolder, view='person-1/mails/10')

    @browsing
    def test_raise_not_found_if_mailaddress_is_not_linked_to_the_given_context(self, browser):
        other_contact = create(Builder('person')
                               .having(firstname=u'Peter', lastname=u'M\xfcller'))
        email = create(Builder('mailaddress')
                       .for_contact(other_contact)
                       .labeled(u'Home')
                       .having(address=u'peter@example.com'))

        with self.assertRaises(NotFound):
            browser.login().visit(
                self.contactfolder,
                view='person-1/mails/{}'.format(email.mailaddress_id))

    @browsing
    def test_returns_view_if_mailaddress_found_on_given_context(self, browser):
        email = create(Builder('mailaddress')
                       .for_contact(self.contact)
                       .labeled(u'Home')
                       .having(address=u'peter@example.com'))

        browser.login().visit(
            self.contactfolder,
            view='person-1/mails/{}'.format(email.mailaddress_id))

        self.assertEqual(
            '{}/person-1/mails/1'.format(self.contactfolder.absolute_url()),
            browser.url)
