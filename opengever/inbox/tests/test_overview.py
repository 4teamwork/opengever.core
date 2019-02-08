from DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.globalindex.handlers.task import sync_task
from opengever.testing import FunctionalTestCase
import transaction


class TestBaseInboxOverview(FunctionalTestCase):

    use_default_fixture = False

    def setUp(self):
        super(TestBaseInboxOverview, self).setUp()

        self.user2, self.org_unit2, self.admin_unit2 = create(
            Builder('fixture')
            .with_user(userid='hans.muster')
            .with_org_unit(unit_id=u'org-unit-2')
            .with_admin_unit(unit_id=u'admin-unit-2'))

        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

        self.inbox = create(Builder('inbox').titled(u'eingangskorb'))


class TestInboxOverviewDocumentBox(TestBaseInboxOverview):

    @browsing
    def test_overview(self, browser):
        browser.login().open(self.inbox, view='tabbedview_view-overview')

    @browsing
    def test_inbox_documents_are_listed(self, browser):
        create(Builder('document')
               .titled('inbox document')
               .with_modification_date(DateTime(2015, 6, 12))
               .within(self.inbox))
        create(Builder('document')
               .titled('portal document')
               .within(self.portal))
        create(Builder('mail')
               .titled('A mail')
               .with_modification_date(DateTime(2015, 6, 10))
               .within(self.inbox))

        browser.login().open(self.inbox, view='tabbedview_view-overview')

        self.assertSequenceEqual(
            browser.css('#documentsBox li:not(.moreLink) a').text,
            ['inbox document', 'A mail'])

    @browsing
    def test_list_only_documents_directly_inside_the_current_inbox(self, browser):
        create(Builder('document')
               .titled('inbox document')
               .within(self.inbox))
        forwarding = create(Builder('forwarding').within(self.inbox))
        create(Builder('document')
               .titled('forwarding document')
               .within(forwarding))

        browser.login().open(self.inbox, view='tabbedview_view-overview')

        self.assertSequenceEqual(
            browser.css('#documentsBox li:not(.moreLink) a').text,
            ['inbox document'])

    @browsing
    def test_document_box_items_are_limited_to_ten_and_sorted_by_modified(self, browser):
        for i in range(1, 11):
            create(Builder('document')
                   .within(self.inbox)
                   .with_modification_date(DateTime(2010, 1, 1) + i)
                   .titled(u'Document %s' % i))
        create(Builder('document')
               .within(self.inbox)
               .with_modification_date(DateTime(2009, 12, 8))
               .titled(u'Document 11'))

        browser.login().open(self.inbox, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            browser.css('#documentsBox li:not(.moreLink) a').text,
            ['Document 10', 'Document 9', 'Document 8', 'Document 7',
             'Document 6', 'Document 5', 'Document 4', 'Document 3',
             'Document 2', 'Document 1'])

    @browsing
    def test_document_box_items_display_bumblebee_tootlip(self, browser):
        document = create(Builder('document')
                          .titled('inbox document')
                          .within(self.inbox))

        browser.login().open(self.inbox, view='tabbedview_view-overview')

        document_nodes = browser.css('#documentsBox li:not(.moreLink) div')
        self.assertEqual(1, len(document_nodes))

        document_node = document_nodes[0]
        self.assertEqual("linkWrapper tooltip-trigger",
                         document_node.get("class"))
        self.assertEqual("/".join((document.absolute_url(), "tooltip")),
                         document_node.get("data-tooltip-url"))


class TestInboxOverviewAssignedInboxTasks(TestBaseInboxOverview):

    @browsing
    def test_list_tasks_and_forwardings_assigned_to_current_inbox_group(self, browser):
        create(Builder('task')
               .within(self.inbox)
               .with_modification_date(DateTime(2014, 1, 1))
               .having(responsible='inbox:org-unit-1')
               .titled(u'Task x'))
        create(Builder('forwarding')
               .within(self.inbox)
               .with_modification_date(DateTime(2014, 1, 2))
               .having(responsible='inbox:org-unit-1')
               .titled(u'Forwarding x'))
        create(Builder('forwarding').having(responsible='inbox:org-unit-2')
                                    .titled(u'Forwarding Invisible'))

        browser.login().open(self.inbox, view='tabbedview_view-overview')
        self.assertEquals(
            ['Forwarding x', 'Task x'],
            browser.css('#assigned_inbox_tasksBox li:not(.moreLink) span span').text)

    @browsing
    def test_task_box_items_are_limited_to_five_and_sorted_by_modified(self, browser):
        for i in range(1, 6):
            create(Builder('forwarding')
                   .within(self.inbox)
                   .having(responsible='inbox:org-unit-1')
                   .with_modification_date(DateTime(2010, 1, 1) + i)
                   .titled(u'Task %s' % i))
        create(Builder('task')
               .within(self.inbox)
               .having(responsible='inbox:org-unit-1')
               .with_modification_date(DateTime(2009, 12, 1))
               .titled(u'Task 6'))

        browser.login().open(self.inbox, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            browser.css('#assigned_inbox_tasksBox li:not(.moreLink) span span').text,
            ['Task 5', 'Task 4', 'Task 3', 'Task 2', 'Task 1'])

    @browsing
    def test_lists_only_the_local_one_when_having_predecessor_successor_couples(self, browser):
        predecessor = create(Builder('forwarding')
                             .having(responsible='inbox:org-unit-2',
                                     assigned_client='org-unit-2')
                             .titled(u'Predecessor'))
        create(Builder('forwarding')
               .having(responsible='inbox:org-unit-1',
                       assigned_client='org-unit-1')
               .successor_from(predecessor)
               .titled(u'Successor'))

        browser.login().open(self.inbox, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            browser.css('#assigned_inbox_tasksBox li:not(.moreLink) span span').text,
            ['Successor'])

    @browsing
    def test_list_only_active_tasks(self, browser):
        create(Builder('forwarding')
               .having(responsible='inbox:org-unit-1')
               .titled('Active'))
        closed = create(Builder('forwarding')
                        .having(responsible='inbox:org-unit-1')
                        .in_state('forwarding-state-closed')
                        .titled('Closed'))
        sync_task(closed, None)
        transaction.commit()

        browser.login().open(self.inbox, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            browser.css('#assigned_inbox_tasksBox li:not(.moreLink) span span').text,
            ['Active'])


class TestInboxOverviewIssuedInboxTasks(TestBaseInboxOverview):

    @browsing
    def test_list_tasks_and_forwardings_issued_by_current_inbox_group(self, browser):
        create(Builder('task')
               .with_modification_date(DateTime(2014, 1, 1))
               .within(self.inbox)
               .having(issuer='inbox:org-unit-1')
               .titled('A Task'))
        create(Builder('forwarding')
               .with_modification_date(DateTime(2014, 2, 1))
               .within(self.inbox)
               .having(issuer='inbox:org-unit-1')
               .titled('A Forwarding'))
        create(Builder('forwarding').having(issuer='inbox:org-unit-2'))

        browser.login().open(self.inbox, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            browser.css('#issued_inbox_tasksBox li:not(.moreLink) span span').text,
            ['A Forwarding', 'A Task'])

    @browsing
    def test_task_box_items_are_limited_to_five_and_sorted_by_modified(self, browser):
        for i in range(1, 6):
            create(Builder('forwarding')
                   .within(self.inbox)
                   .having(issuer='inbox:org-unit-1')
                   .with_modification_date(DateTime(2010, 1, 1) + i)
                   .titled(u'Task %s' % i))
        create(Builder('task')
               .within(self.inbox)
               .having(issuer='inbox:org-unit-1')
               .with_modification_date(DateTime(2009, 12, 1))
               .titled(u'Task 6'))

        browser.login().open(self.inbox, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            browser.css('#issued_inbox_tasksBox li:not(.moreLink) span span').text,
            ['Task 5', 'Task 4', 'Task 3', 'Task 2', 'Task 1'])

    @browsing
    def test_list_only_active_tasks(self, browser):
        create(Builder('forwarding')
               .having(issuer='inbox:org-unit-1')
               .titled('Active'))
        closed = create(Builder('forwarding')
                        .having(issuer='inbox:org-unit-1')
                        .in_state('forwarding-state-closed')
                        .titled('Closed'))
        sync_task(closed, None)
        transaction.commit()

        browser.login().open(self.inbox, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            browser.css('#issued_inbox_tasksBox li:not(.moreLink) span span').text,
            ['Active'])
