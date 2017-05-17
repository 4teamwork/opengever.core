from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from ftw.testbrowser.pages.factoriesmenu import addable_types
from opengever.testing import FunctionalTestCase


class TestForwarding(FunctionalTestCase):

    def setUp(self):
        super(TestForwarding, self).setUp()
        self.inbox = create(Builder('inbox'))

    @browsing
    def test_forwarding_is_not_addable_over_the_factory_menu(self, browser):
        browser.login().open(self.inbox)

        self.assertEqual(['Document'], addable_types(browser))

    @browsing
    def test_at_least_one_document_references_is_required(self, browser):
        browser.login().open(
            self.inbox, view='++add++opengever.inbox.forwarding')

        messages = statusmessages.messages()
        self.assertEqual(
            ['Error: Please select at least one document to forward.'],
            messages.get('error'))

    @browsing
    def test_creation_moves_document_in_to_the_forwarding(self, browser):
        doc1 = create(Builder('document').within(self.inbox).titled(u'Doc 1'))
        doc2 = create(Builder('document').within(self.inbox).titled(u'Doc 2'))
        doc3 = create(Builder('document').within(self.inbox).titled(u'Doc 3'))

        data = {'paths': ['/'.join(doc.getPhysicalPath()) for doc in [doc1, doc3]]}

        browser.login().open(self.inbox, data,
                             view='++add++opengever.inbox.forwarding')

        browser.fill({'Title': u'Test forwarding',
                      'Responsible': 'inbox:client1'})
        browser.css('#form-buttons-save').first.click()

        forwarding = self.inbox.get('forwarding-1')
        self.assertEqual(['Item created'], statusmessages.messages().get('info'))
        self.assertEqual([doc1, doc3], forwarding.listFolderContents())
        self.assertEqual([doc2], self.inbox.listFolderContents(
            {'portal_type': 'opengever.document.document'}))

    @browsing
    def test_forwarding_add_form_does_not_render_empty_fieldset_additional(self, browser):
        doc = create(Builder('document').within(self.inbox).titled(u'Doc 1'))
        data = dict(paths=[doc.getPhysicalPath()])

        browser.login().open(self.inbox, data,
                             view='++add++opengever.inbox.forwarding')

        fieldsets = browser.css('form#form fieldset')
        self.assertEqual(1, len(fieldsets))
        self.assertEqual('Common', fieldsets.first.css('legend').first.text)

    @browsing
    def test_forwarding_edit_form_does_not_render_empty_fieldset_additional(self, browser):
        forwarding = create(Builder('forwarding').within(self.inbox))

        self.grant('Manager')
        browser.login().open(forwarding, view='edit')

        fieldsets = browser.css('form#form fieldset')
        self.assertEqual(1, len(fieldsets))
        self.assertEqual('Common', fieldsets.first.css('legend').first.text)
