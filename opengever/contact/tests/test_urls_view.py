from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.contact.browser.related_entity import IRelatedEntityCRUDActions
from opengever.contact.browser.urls import URLsView
from opengever.contact.models import URL
from opengever.testing import FunctionalTestCase
from zope.interface.verify import verifyClass


class TestURLsView(FunctionalTestCase):

    def setUp(self):
        super(TestURLsView, self).setUp()
        self.contactfolder = create(Builder('contactfolder'))
        self.contact = create(Builder('person')
                              .having(firstname=u'Peter',
                                      lastname=u'M\xfcller'))

    def test_verify_interface(self):
        self.assertTrue(verifyClass(IRelatedEntityCRUDActions, URLsView))

    @browsing
    def test_add_url(self, browser):
        browser.login().visit(
            self.contactfolder,
            {'label': 'Private', 'url': 'http://www.example.com/peter'},
            view='person-1/urls/add')

        url = URL.query.first()

        self.assertEqual('Private', url.label)
        self.assertEqual('http://www.example.com/peter', url.url)

        self.assertDictContainsSubset({
            'message': 'The object was added successfully',
            'messageClass': 'info'},
            browser.json.get('messages')[0])

        self.assertDictContainsSubset({u'proceed': True}, browser.json)

    @browsing
    def test_add_url_without_url_returns_validation_error(self, browser):
        browser.login().visit(self.contactfolder, data={'label': 'Private'},
                              view='person-1/urls/add')

        self.assertEquals(0, URL.query.count())
        self.assertDictContainsSubset(
            {'message': 'Please specify an url',
             'messageClass': 'error'},
            browser.json.get('messages')[0])

    @browsing
    def test_lists_multiple_urls(self, browser):
        create(Builder('url')
               .for_contact(self.contact)
               .having(
                   label=u'Private',
                   url=u'http://www.example.com/peter'))
        create(Builder('url')
               .for_contact(self.contact)
               .having(
                   label=u'Business',
                   url=u'http://www.example.com/peter-business'))

        browser.login().visit(self.contactfolder,
                              view='person-1/urls/list')

        item1, item2 = browser.json.get('objects')
        self.assertDictContainsSubset(
            {u'url': u'http://www.example.com/peter',
             u'label': u'Private',
             u'contact_id': 1,
             u'id': 1},
            item1)
        self.assertDictContainsSubset(
            {u'url': u'http://www.example.com/peter-business',
             u'label': u'Business',
             u'contact_id': 1,
             u'id': 2},
            item2)

    @browsing
    def test_delete_given_url(self, browser):
        create(Builder('url').for_contact(self.contact))

        self.assertEqual(1, URL.query.count())

        browser.login().visit(self.contactfolder,
                              view='person-1/urls/1/delete')

        self.assertDictContainsSubset(
            {'message': 'Object successfully deleted',
             'messageClass': 'info'},
            browser.json.get('messages')[0])

        self.assertEqual(0, URL.query.count())

    @browsing
    def test_update_label_and_url_of_existing_url(self, browser):
        create(Builder('url')
               .for_contact(self.contact)
               .having(
                   label=u'Private',
                   url=u'http://www.example.com/peter'))

        browser.login().visit(
            self.contactfolder,
            {'label': 'Business', 'url': u'http://www.example.ch/peter'},
            view='person-1/urls/1/update')

        url = URL.query.first()

        self.assertEqual('Business', url.label)
        self.assertEqual(u'http://www.example.ch/peter', url.url)

        self.assertDictContainsSubset(
            {'message': 'Object updated.', 'messageClass': 'info'},
            browser.json.get('messages')[0])
