from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.testing import select_current_org_unit
from opengever.trash.trash import Trasher


class TestInboxTabbedview(IntegrationTestCase):

    @browsing
    def test_trash_listing_does_not_contain_subdossier_and_checked_out_column(self, browser):
        self.login(self.secretariat_user, browser=browser)

        Trasher(self.inbox_document).trash()
        browser.open(self.inbox, view='tabbedview_view-trash')

        self.assertEquals(
            ['', 'Sequence Number', 'Title', 'Document Author',
             'Document Date', 'Modification Date', 'Creation Date',
             'Receipt Date', 'Delivery Date', 'Public Trial',
             'Reference Number'],
            browser.css('.listing th').text)

    @browsing
    def test_document_listings_does_not_contain_subdossier_checked_out_and_reference_column(self, browser):
        self.login(self.secretariat_user, browser=browser)

        browser.open(self.inbox, view='tabbedview_view-documents')

        self.assertEquals(
            ['', 'Sequence Number', 'Title', 'Document Author',
             'Document Date', 'Modification Date', 'Creation Date',
             'Receipt Date', 'Delivery Date', 'Public Trial'],
            browser.css('.listing th').text)

    @browsing
    def test_add_task_and_proposal_action_are_hidden(self, browser):
        self.login(self.secretariat_user, browser=browser)

        browser.open(self.inbox, view='tabbedview_view-documents')

        self.assertNotIn(
            'Create Proposal', browser.css('#tabbedview-menu a').text)
        self.assertNotIn(
            'Create Task', browser.css('#tabbedview-menu a').text)


class TestAssignedInboxTaskTab(IntegrationTestCase):

    viewname = 'assigned_inbox_tasks'

    def test_lists_only_tasks_assigned_to_the_current_org_units_inbox(self):
        self.login(self.secretariat_user)

        self.add_additional_org_unit()

        self.inbox_forwarding.responsible = 'inbox:fa'
        self.inbox_forwarding.sync()

        view = self.inbox.restrictedTraverse(
            'tabbedview_view-{}'.format(self.viewname))
        view.update()

        self.assertEquals(
            [self.inbox_forwarding.get_sql_object()], view.contents)

        select_current_org_unit('additional')
        view.update()
        self.assertEquals([], view.contents)

    def test_list_tasks_assigned_to_current_inbox(self):
        self.login(self.secretariat_user)

        self.task.responsible = 'inbox:fa'
        self.task.sync()

        view = self.inbox.restrictedTraverse(
            'tabbedview_view-{}'.format(self.viewname))
        view.update()

        self.assertEquals([self.task.get_sql_object()], view.contents)


class TestIssuedInboxTaskTab(IntegrationTestCase):

    viewname = 'issued_inbox_tasks'

    def test_list_tasks_and_forwardings(self):
        self.login(self.secretariat_user)

        self.task.issuer = 'inbox:fa'
        self.task.sync()

        self.inbox_forwarding.issuer = 'inbox:fa'
        self.inbox_forwarding.sync()

        view = self.inbox.restrictedTraverse(
            'tabbedview_view-{}'.format(self.viewname))
        view.update()

        self.assertItemsEqual(
            [self.task.get_sql_object(), self.inbox_forwarding.get_sql_object()],
            view.contents)

    def test_list_only_task_with_current_org_units_inbox_as_a_issuer(self):
        self.login(self.secretariat_user)

        view = self.inbox.restrictedTraverse(
            'tabbedview_view-{}'.format(self.viewname))
        view.update()

        self.assertEquals([], view.contents)

        self.inbox_forwarding.issuer = 'inbox:fa'
        self.inbox_forwarding.sync()
        view.update()

        self.assertEquals(
            [self.inbox_forwarding.get_sql_object()],
            view.contents)


class TestClosedForwardings(IntegrationTestCase):

    @browsing
    def test_state_filter_is_deactivated(self, browser):
        self.login(self.manager)
        yearfolder = create(Builder('yearfolder').titled(u'2018'))
        create(Builder('forwarding')
               .having(responsible_client='fa',
                       responsible=self.regular_user.getId(),
                       issuer=self.dossier_responsible.getId())
               .within(yearfolder)
               .in_state('forwarding-state-closed')
               .titled('Closed Forwarding'))

        self.login(self.regular_user, browser=browser)
        browser.open(yearfolder, view='tabbedview_view-closed-forwardings')

        self.assertEquals([], browser.css('.state_filters'))
        self.assertEquals(u'Closed Forwarding', browser.css('.listing a').first.text)
