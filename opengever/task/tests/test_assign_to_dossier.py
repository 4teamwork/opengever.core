from Acquisition import aq_parent
from datetime import date
from ftw.testbrowser import browsing
from opengever.testing import SolrIntegrationTestCase


class TestAssignForwardingToDossier(SolrIntegrationTestCase):

    @browsing
    def test_assign_to_new_dossier(self, browser):
        self.login(self.secretariat_user, browser=browser)

        forwarding = self.inbox_forwarding
        document = self.inbox_forwarding_document
        responsible = self.regular_user.getId()

        browser.open(forwarding)
        browser.css('#workflow-transition-forwarding-transition-assign-to-dossier').first.click()

        # Step 1 - choose method
        browser.fill(
            {'Assign to a ...': 'new_dossier',
             'Response': 'Sample response'}).submit()

        # Step 2 - choose repository
        browser.fill({
            'form.widgets.repositoryfolder.widgets.query': self.leaf_repofolder.Title()
        }).submit()
        browser.fill({'form.widgets.repositoryfolder':
                      '/'.join(self.leaf_repofolder.getPhysicalPath())})
        browser.css('#form-buttons-save').first.click()

        # Step 3 - dossier add form
        browser.fill({'Title': 'My new dossier'})
        browser.css('#form-buttons-save').first.click()

        # Step 4 - edit task form
        browser.fill({'Task Type': 'comment',
                      'Deadline': '9/24/14',
                      'Issuer': 'inbox:fa'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(responsible)

        browser.css('#form-buttons-save').first.click()

        # Assertions
        self.assertEquals(forwarding.Title().decode('utf8'), browser.context.title,
                          'Forwarding title should be assumed to the new task')
        self.assertEquals(responsible, browser.context.responsible)
        self.assertEquals('inbox:fa', browser.context.issuer)

        self.assertEquals(document.Title(),
                          browser.context.listFolderContents()[0].Title(),
                          'The forwarded document is not copied to task')

        self.assertEquals('My new dossier', aq_parent(browser.context).title)

        yearfolder = self.inbox.get(str(date.today().year))
        self.assertEquals(
            forwarding, yearfolder.get('forwarding-1'),
            'The forwarding was not correctly moved in to the actual yearfolder')

    @browsing
    def test_assign_to_existing_dossier(self, browser):
        self.login(self.secretariat_user, browser=browser)

        forwarding = self.inbox_forwarding
        document = self.inbox_forwarding_document
        responsible = self.regular_user.getId()

        # dossier = create(Builder('dossier').titled(u'Dossier A'))

        browser.open(forwarding)
        browser.css('#workflow-transition-forwarding-transition-assign-to-dossier').first.click()

        # Step 1 - choose method
        browser.fill(
            {'Assign to a ...': 'existing_dossier',
             'Response': 'Sample response'}).submit()

        # Step 2 - choose dossier
        browser.fill(
            {'form.widgets.dossier.widgets.query': self.dossier.Title()}).submit()
        browser.fill({'form.widgets.dossier': '/'.join(self.dossier.getPhysicalPath())})
        browser.css('#form-buttons-save').first.click()

        # Step 3 - edit task form
        browser.fill({'Task Type': 'comment',
                      'Deadline': '9/24/14',
                      'Issuer': 'inbox:fa'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(responsible)

        browser.css('#form-buttons-save').first.click()

        # Assertions
        self.assertEquals(forwarding.title, browser.context.title,
                          'Forwarding title should be assumed to the new task')
        self.assertEquals(responsible, browser.context.responsible)
        self.assertEquals('inbox:fa', browser.context.issuer)

        self.assertEquals(document.Title(),
                          browser.context.listFolderContents()[0].Title(),
                          'The forwarded document is not copied to task')

        self.assertEquals(self.dossier, aq_parent(browser.context))

        yearfolder = self.inbox.get(str(date.today().year))
        self.assertEquals(
            forwarding, yearfolder.get('forwarding-1'),
            'The forwarding was not correctly moved in to the actual yearfolder')
