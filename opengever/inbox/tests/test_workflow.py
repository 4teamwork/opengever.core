from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from plone import api


class TestInboxWorkflow(IntegrationTestCase):

    features = (
        '!officeconnector-checkout',
    )

    @browsing
    def test_only_managers_are_able_to_edit_inboxes(self, browser):
        self.login(self.secretariat_user, browser=browser)
        with browser.expect_unauthorized():
            browser.open(self.inbox, view='edit')

        self.login(self.administrator, browser=browser)
        with browser.expect_unauthorized():
            browser.open(self.inbox, view='edit')

        self.login(self.manager, browser=browser)
        browser.open(self.inbox, view='edit')
        browser.fill({'Title': 'Eingangskorb 1'})
        browser.click_on('Save')

        self.assertEquals(200, browser.status_code)

    def test_inbox_documents_uses_placeful_workflow(self):
        self.login(self.secretariat_user)

        wftool = api.portal.get_tool('portal_workflow')
        self.assertEquals(
            'opengever_inbox_document_workflow',
            wftool.getWorkflowsFor(self.inbox_document)[0].id)

    @browsing
    def test_editors_are_able_to_edit_and_checkout_a_document(self, browser):
        self.login(self.secretariat_user, browser=browser)

        browser.open(self.inbox_document, view='edit')
        browser.fill({'Title': 'Document Update'})
        browser.click_on('Save')

        self.assertEquals(200, browser.status_code)

        browser.open(self.inbox_document, view='tabbedview_view-overview')
        browser.click_on('Checkout and edit')

        self.assertEquals(200, browser.status_code)
        self.assertEquals(self.secretariat_user.id,
                          self.inbox_document.checked_out_by())

    def test_switch_to_regular_workflow_when_moving_a_document_to_repository(self):
        self.login(self.secretariat_user)

        moved = api.content.move(
            source=self.inbox_document, target=self.dossier)

        wftool = api.portal.get_tool('portal_workflow')
        self.assertEquals(
            'opengever_document_workflow',
            wftool.getWorkflowsFor(moved)[0].id)

    @browsing
    def test_switch_to_regular_workflow_when_assign_to_dossier_via_forwarding(self, browser):
        self.login(self.secretariat_user, browser=browser)

        # step 1
        browser.open(self.inbox_forwarding, view='tabbedview_view-overview')
        browser.click_on('forwarding-transition-assign-to-dossier')
        browser.fill({'Assign to a ...': 'existing_dossier',
                      'Response': 'Sample response'}).submit()
        # step 2
        browser.fill(
            {'form.widgets.dossier.widgets.query': 'Finanzverwaltung'}).submit()
        browser.fill(
            {'form.widgets.dossier': '/'.join(self.dossier.getPhysicalPath())})
        browser.click_on('Save')
        # step 3
        browser.click_on('Save')

        document, = browser.context.objectValues()
        wftool = api.portal.get_tool('portal_workflow')
        self.assertEquals('opengever_document_workflow',
                          wftool.getWorkflowsFor(document)[0].id)
