from Acquisition import aq_parent
from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestAssignForwardignToDossier(FunctionalTestCase):

    use_default_fixture = False

    def setUp(self):
        super(TestAssignForwardignToDossier, self).setUp()

        create(Builder('fixture')
               .with_user()
               .with_org_unit()
               .with_admin_unit(public_url=self.portal.absolute_url()))

        self.inbox = create(Builder('inbox'))
        self.forwarding = create(Builder('forwarding')
                                 .titled(u'A letter from peter')
                                 .within(self.inbox))
        self.document = create(Builder('document')
                               .titled(u'The letter')
                               .with_dummy_content()
                               .within(self.forwarding))

        self.repo_root = create(Builder('repository_root'))
        self.repo_folder = create(Builder('repository')
                                  .titled('Repo A')
                                  .within(self.repo_root))

    @browsing
    def test_assign_to_new_dossier(self, browser):
        browser.login().open(self.forwarding)
        browser.css('#workflow-transition-forwarding-transition-assign-to-dossier').first.click()

        # Step 1 - choose method
        browser.fill(
            {'Assign to a ...': 'new_dossier',
             'Response': 'Sample response'}).submit()

        # Step 2 - choose repository
        browser.fill(
            {'form.widgets.repositoryfolder.widgets.query': 'Repo A'}).submit()
        browser.fill({'form.widgets.repositoryfolder':
                      '/plone/ordnungssystem/repo-a'})
        browser.css('#form-buttons-save').first.click()

        # Step 3 - dossier add form
        browser.fill({'Title': 'My new dossier'})
        browser.css('#form-buttons-save').first.click()

        # Step 4 - edit task form
        browser.fill({'Task Type': 'comment',
                      'Deadline': '9/24/14',
                      'Issuer': 'inbox:org-unit-1'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(TEST_USER_ID)

        browser.css('#form-buttons-save').first.click()

        # Assertions
        self.assertEquals('A letter from peter', browser.context.title,
                          'Forwarding title should be assumed to the new task')
        self.assertEquals(TEST_USER_ID, browser.context.responsible)
        self.assertEquals('inbox:org-unit-1', browser.context.issuer)

        self.assertEquals('The letter',
                          browser.context.listFolderContents()[0].Title(),
                          'The forwarded document is not copied to task')

        self.assertEquals('My new dossier', aq_parent(browser.context).title)

        yearfolder = self.inbox.get(str(date.today().year))
        self.assertEquals(
            self.forwarding, yearfolder.get('forwarding-1'),
            'The forwarding was not correctly moved in to the actual yearfolder')

    @browsing
    def test_assign_to_existing_dossier(self, browser):
        dossier = create(Builder('dossier').titled(u'Dossier A'))

        browser.login().open(self.forwarding)
        browser.css('#workflow-transition-forwarding-transition-assign-to-dossier').first.click()

        # Step 1 - choose method
        browser.fill(
            {'Assign to a ...': 'existing_dossier',
             'Response': 'Sample response'}).submit()

        # Step 2 - choose dossier
        browser.fill(
            {'form.widgets.dossier.widgets.query': 'Dossier A'}).submit()
        browser.fill({'form.widgets.dossier': '/plone/dossier-1'})
        browser.css('#form-buttons-save').first.click()

        # Step 3 - edit task form
        browser.fill({'Task Type': 'comment',
                      'Deadline': '9/24/14',
                      'Issuer': 'inbox:org-unit-1'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(TEST_USER_ID)

        browser.css('#form-buttons-save').first.click()

        # Assertions
        self.assertEquals('A letter from peter', browser.context.title,
                          'Forwarding title should be assumed to the new task')
        self.assertEquals(TEST_USER_ID, browser.context.responsible)
        self.assertEquals('inbox:org-unit-1', browser.context.issuer)

        self.assertEquals('The letter',
                          browser.context.listFolderContents()[0].Title(),
                          'The forwarded document is not copied to task')

        self.assertEquals(dossier, aq_parent(browser.context))

        yearfolder = self.inbox.get(str(date.today().year))
        self.assertEquals(
            self.forwarding, yearfolder.get('forwarding-1'),
            'The forwarding was not correctly moved in to the actual yearfolder')
