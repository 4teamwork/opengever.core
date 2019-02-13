from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from ftw.testbrowser.pages.factoriesmenu import addable_types
from opengever.testing import IntegrationTestCase


class TestForwarding(IntegrationTestCase):

    @browsing
    def test_forwarding_is_not_addable_over_the_factory_menu(self, browser):
        self.login(self.secretariat_user, browser=browser)
        browser.open(self.inbox)

        self.assertEqual(['Document'], addable_types(browser))

    @browsing
    def test_at_least_one_document_references_is_required(self, browser):
        self.login(self.secretariat_user, browser=browser)
        browser.open(self.inbox,
                     view='++add++opengever.inbox.forwarding')

        messages = statusmessages.messages()
        self.assertEqual(
            ['Error: Please select at least one document to forward.'],
            messages.get('error'))

    @browsing
    def test_creation_moves_document_in_to_the_forwarding(self, browser):
        self.login(self.secretariat_user, browser=browser)

        doc1 = create(Builder('document').within(self.inbox).titled(u'Doc 1'))
        doc2 = create(Builder('document').within(self.inbox).titled(u'Doc 2'))
        doc3 = create(Builder('document').within(self.inbox).titled(u'Doc 3'))

        data = {
            'paths': ['/'.join(doc.getPhysicalPath()) for doc in [doc1, doc3]]}

        browser.open(
            self.inbox, data, view='++add++opengever.inbox.forwarding')
        browser.fill({'Title': u'Test forwarding',
                      'Responsible': 'inbox:fa'})
        browser.css('#form-buttons-save').first.click()

        forwarding = self.inbox.objectValues()[-1]

        self.assertEqual(['Item created'],
                         statusmessages.messages().get('info'))
        self.assertEqual([doc1, doc3], forwarding.listFolderContents())
        self.assertIn(doc2, self.inbox.listFolderContents())

    @browsing
    def test_forwarding_add_form_does_not_render_empty_fieldset_additional(
            self, browser):

        self.login(self.secretariat_user, browser=browser)

        data = self.make_path_param(self.inbox_document)
        browser.open(
            self.inbox, data, view='++add++opengever.inbox.forwarding')

        fieldsets = browser.css('form#form fieldset')
        self.assertEqual(1, len(fieldsets))
        self.assertEqual('Common', fieldsets.first.css('legend').first.text)

    @browsing
    def test_forwarding_edit_form_does_not_render_empty_fieldset_additional(
            self, browser):

        self.login(self.manager, browser=browser)
        browser.open(self.inbox_forwarding, view='edit')

        fieldsets = browser.css('form#form fieldset')
        self.assertEqual(1, len(fieldsets))
        self.assertEqual('Common', fieldsets.first.css('legend').first.text)

    @browsing
    def test_teams_are_available_as_responsible(self, browser):
        self.login(self.secretariat_user, browser=browser)

        data = self.make_path_param(self.inbox_document)
        browser.open(
            self.inbox, data, view='++add++opengever.inbox.forwarding')
        browser.fill({'Title': u'Test forwarding'})

        # Fill responsible manually
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('team:1')
        browser.find('Save').click()

        forwarding = browser.context.objectValues()[-1]

        self.assertEqual('team:1', forwarding.responsible)
        self.assertEqual(u'Test forwarding', forwarding.title)

    @browsing
    def test_forwarding_can_reassigned_to_a_team(self, browser):
        self.login(self.secretariat_user, browser=browser)
        browser.open(self.inbox_forwarding)
        browser.click_on('forwarding-transition-reassign')

        # Fill responsible manually
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('team:1')
        browser.click_on('Assign')

        self.assertEqual('team:1', self.inbox_forwarding.responsible)

        browser.open(self.inbox_forwarding, view='tabbedview_view-overview')
        responsible_row = browser.css('.listing').first.rows[8]
        self.assertEqual(['Responsible'], responsible_row.css('th').text)
        self.assertEqual([u'Projekt \xdcberbaung Dorfmatte (Finanz\xe4mt)'],
                         responsible_row.css('td').text)

    @browsing
    def test_is_private_field_respects_feature_flag(self, browser):
        self.login(self.secretariat_user, browser=browser)
        data = {'paths': ['/'.join(self.inbox_document.getPhysicalPath())]}

        browser.open(
            self.inbox, data, view='++add++opengever.inbox.forwarding')
        self.assertIn('Private task', browser.forms['form'].field_labels)

        self.deactivate_feature('private-tasks')
        browser.open(self.inbox, data, view='++add++opengever.inbox.forwarding')
        self.assertNotIn('Private task', browser.forms['form'].field_labels)
