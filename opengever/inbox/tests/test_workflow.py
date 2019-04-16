from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.role_assignments import ASSIGNMENT_VIA_TASK
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import index_data_for
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

        mail = create(Builder('mail').within(self.inbox_forwarding))

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

        document, mail = browser.context.objectValues()
        wftool = api.portal.get_tool('portal_workflow')
        self.assertEquals('opengever_document_workflow',
                          wftool.getWorkflowsFor(document)[0].id)
        self.assertEquals('opengever_mail_workflow',
                          wftool.getWorkflowsFor(mail)[0].id)

    def test_inbox_mail_uses_placeful_workflow(self):
        self.login(self.secretariat_user)

        mail = create(Builder('mail').within(self.inbox))

        wftool = api.portal.get_tool('portal_workflow')
        self.assertEquals(
            'opengever_inbox_mail_workflow',
            wftool.getWorkflowsFor(mail)[0].id)

    @browsing
    def test_editors_are_able_to_edit_a_mail(self, browser):
        self.login(self.secretariat_user, browser=browser)

        mail = create(Builder('mail').within(self.inbox))

        browser.open(mail, view='edit')
        browser.fill({'Title': 'Mail Update'})
        browser.click_on('Save')

        self.assertEquals(200, browser.status_code)
        self.assertEqual("Mail Update", mail.Title())

    def test_switch_to_regular_workflow_when_moving_a_mail_to_repository(self):
        self.login(self.secretariat_user)

        mail = create(Builder('mail').within(self.inbox))

        moved = api.content.move(
            source=mail, target=self.dossier)

        wftool = api.portal.get_tool('portal_workflow')
        self.assertEquals(
            'opengever_mail_workflow',
            wftool.getWorkflowsFor(moved)[0].id)

    def test_local_roles_assigned_properly_when_creating_forwarding(self):
        self.login(self.secretariat_user)

        self.forwarding = create(
            Builder('forwarding')
            .within(self.inbox)
            .titled(u'Test forwarding')
            .having(responsible_client='fa',
                    responsible=self.secretariat_user.getId(),
                    issuer=self.secretariat_user.getId())
            .relate_to(self.inbox_document))

        # Editor role is granted to forwarding responsible
        assignment_manager = RoleAssignmentManager(self.forwarding)
        assignments = assignment_manager.storage._storage()
        self.assertEqual(1, len(assignments))
        assignment = assignments[0]
        self.assertEqual(ASSIGNMENT_VIA_TASK, assignment["cause"])
        self.assertEqual(["Editor"], assignment["roles"])
        self.assertEqual(self.secretariat_user.getId(), assignment["principal"])

        # No role assignments on contained objects as they already
        # inherit from the forwarding
        inbox_document, = self.forwarding.listFolderContents()
        assignment_manager = RoleAssignmentManager(inbox_document)
        assignments = assignment_manager.storage._storage()
        self.assertEqual(0, len(assignments))

    @browsing
    def test_assign_updates_role_assignment_on_forwarding(self, browser):
        self.login(self.secretariat_user, browser)

        assignment_manager = RoleAssignmentManager(self.inbox_forwarding)
        assignments = assignment_manager.storage._storage()
        self.assertEqual(2, len(assignments))
        assignment = assignments[0]
        self.assertEqual(ASSIGNMENT_VIA_TASK, assignment["cause"])
        self.assertEqual(["Editor"], assignment["roles"])
        self.assertEqual(self.regular_user.getId(), assignment["principal"])

        browser.open(self.inbox_forwarding)
        browser.click_on('forwarding-transition-reassign')
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('fa:{}'.format(self.secretariat_user.getId()))
        browser.click_on('Assign')

        assignment_manager = RoleAssignmentManager(self.inbox_forwarding)
        assignments = assignment_manager.storage._storage()
        self.assertEqual(1, len(assignments))
        assignment = assignments[0]
        self.assertEqual(ASSIGNMENT_VIA_TASK, assignment["cause"])
        self.assertEqual(["Editor"], assignment["roles"])
        self.assertEqual(self.secretariat_user.getId(), assignment["principal"])

    @browsing
    def test_forwarding_grants_view_permissions(self, browser):
        self.login(self.secretariat_user, browser)

        mail = create(Builder('mail').within(self.inbox_forwarding))

        self.assertIn("user:{}".format(self.regular_user),
                      index_data_for(self.inbox_forwarding)['allowedRolesAndUsers'])
        self.assertIn("user:{}".format(self.regular_user),
                      index_data_for(self.inbox_forwarding_document)['allowedRolesAndUsers'])
        self.assertIn("user:{}".format(self.regular_user),
                      index_data_for(mail)['allowedRolesAndUsers'])
        self.assertNotIn("user:{}".format(self.meeting_user),
                         index_data_for(self.inbox_forwarding)['allowedRolesAndUsers'])
        self.assertNotIn("user:{}".format(self.meeting_user),
                         index_data_for(self.inbox_forwarding_document)['allowedRolesAndUsers'])
        self.assertNotIn("user:{}".format(self.meeting_user),
                         index_data_for(mail)['allowedRolesAndUsers'])

        browser.open(self.inbox_forwarding)
        browser.click_on('forwarding-transition-reassign')
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('fa:{}'.format(self.meeting_user.getId()))
        browser.click_on('Assign')

        self.assertNotIn("user:{}".format(self.regular_user),
                         index_data_for(self.inbox_forwarding)['allowedRolesAndUsers'])
        self.assertNotIn("user:{}".format(self.regular_user),
                         index_data_for(self.inbox_forwarding_document)['allowedRolesAndUsers'])
        self.assertNotIn("user:{}".format(self.regular_user),
                         index_data_for(mail)['allowedRolesAndUsers'])
        self.assertIn("user:{}".format(self.meeting_user),
                      index_data_for(self.inbox_forwarding)['allowedRolesAndUsers'])
        self.assertIn("user:{}".format(self.meeting_user),
                      index_data_for(self.inbox_forwarding_document)['allowedRolesAndUsers'])
        self.assertIn("user:{}".format(self.meeting_user),
                      index_data_for(mail)['allowedRolesAndUsers'])
