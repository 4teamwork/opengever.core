from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestTaskOverview(FunctionalTestCase):

    use_default_fixture = False

    def setUp(self):
        super(TestTaskOverview, self).setUp()
        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture')
            .with_user()
            .with_org_unit()
            .with_admin_unit(public_url='http://plone'))

    @browsing
    def test_issuer_is_linked_to_issuers_details_view(self, browser):
        task = create(Builder("task").having(task_type='comment',
                                             issuer=TEST_USER_ID))

        browser.login().open(task, view='tabbedview_view-overview')

        self.assertEquals(
            'http://nohost/plone/@@user-details/test_user_1_',
            browser.css('.issuer a').first.get('href'))

    @browsing
    def test_issuer_is_labeld_by_user_description(self, browser):
        task = create(Builder("task").having(task_type='comment',
                                             issuer=TEST_USER_ID))

        browser.login().open(task, view='tabbedview_view-overview')

        self.assertEquals(
            self.user.label(), browser.css('.issuer a').first.text)

    @browsing
    def test_issuer_is_prefixed_by_current_org_unit_on_a_multiclient_setup(self, browser):
        create(Builder('org_unit').id('client2'))
        task = create(Builder("task").having(task_type='comment',
                                             issuer=TEST_USER_ID))

        browser.login().open(task, view='tabbedview_view-overview')

        self.assertEquals(
            'Client1 / Test User (test_user_1_)',
            browser.css('.issuer').first.text)

    @browsing
    def test_documents_are_listed(self, browser):
        dossier = create(Builder('dossier').titled(u'Dossier'))
        task = create(Builder("task")
                      .within(dossier)
                      .titled(u'Aufgabe')
                      .having(text='Text blabla',
                              task_type='comment',
                              deadline=datetime(2010, 1, 1),
                              issuer=TEST_USER_ID,
                              responsible=TEST_USER_ID))
        document = create(Builder('document')
                          .titled(u'Some document')
                          .within(task))
        browser.login().open(task, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            [u'Some document'],
            browser.css('#documentsBox span.document').text)

    @browsing
    def test_task_overview_displays_task_information(self, browser):
        dossier = create(Builder('dossier').titled(u'Dossier'))
        task = create(Builder("task")
                      .within(dossier)
                      .titled(u'Aufgabe')
                      .having(text='Text blabla',
                              task_type='comment',
                              deadline=datetime(2010, 1, 1),
                              issuer=TEST_USER_ID,
                              responsible=TEST_USER_ID))
        browser.login().open(task, view='tabbedview_view-overview')

        table_data = [
            each[1] for each in
            browser.css('#main_attributesBox table.vertical.listing')
            .first.lists()
        ]

        self.assertSequenceEqual(
            ['Aufgabe', 'Dossier', 'Text blabla', 'To comment',
             'task-state-open', '01.01.2010', self.user.label(),
             self.user.label(), ''],
            table_data
        )

    @browsing
    def test_subtasks_are_shown_on_parent_task_page(self, browser):
        dossier = create(Builder('dossier').titled(u'Dossier'))
        task = create(Builder("task")
                      .within(dossier)
                      .titled(u'Parent')
                      .having(text='Text blabla',
                              task_type='report',
                              deadline=datetime(2010, 1, 1),
                              issuer=TEST_USER_ID,
                              responsible=TEST_USER_ID))
        sub1 = create(Builder("task")
                      .within(task)
                      .titled(u'Subtask 1')
                      .having(task_type='report',
                              issuer=TEST_USER_ID,
                              responsible=TEST_USER_ID))
        sub2 = create(Builder("task")
                      .within(task)
                      .titled(u'Subtask 2')
                      .having(task_type='report',
                                issuer=TEST_USER_ID,
                              responsible=TEST_USER_ID))

        browser.login().open(task, view='tabbedview_view-overview')
        task_list = browser.css('#sub_taskBox div.task').text
        self.assertSequenceEqual(
            ['Subtask 1 ({})'.format(self.user.label()),
             'Subtask 2 ({})'.format(self.user.label())],
            task_list
        )
        self.assertSequenceEqual(
            [], browser.css('#containing_taskBox div.task').text)

    @browsing
    def test_parent_task_is_shown_on_subtask_page(self, browser):
        dossier = create(Builder('dossier').titled(u'Dossier'))
        task = create(Builder("task")
                      .within(dossier)
                      .titled(u'Parent')
                      .having(text='Text blabla',
                              task_type='report',
                              deadline=datetime(2010, 1, 1),
                              issuer=TEST_USER_ID,
                              responsible=TEST_USER_ID))
        sub = create(Builder("task")
                     .within(task)
                     .titled(u'Subtask 1')
                     .having(task_type='report',
                             issuer=TEST_USER_ID,
                             responsible=TEST_USER_ID))

        browser.login().open(sub, view='tabbedview_view-overview')
        task_list = browser.css('#containing_taskBox div.task').text
        self.assertSequenceEqual(
            ['Parent ({})'.format(self.user.label())], task_list)

        self.assertSequenceEqual(
            [], browser.css('#sub_taskBox div.task').text)

    @browsing
    def test_predecessor_successor_tasks_are_shown(self, browser):
        dossier = create(Builder('dossier').titled(u'Dossier'))
        predecessor = create(Builder("task")
                             .within(dossier)
                             .titled(u'Predecessor')
                             .having(text='Text blabla',
                                     task_type='report',
                                     deadline=datetime(2010, 1, 1),
                                     issuer=TEST_USER_ID,
                                     responsible=TEST_USER_ID))
        successor = create(Builder("task")
                           .within(dossier)
                           .titled(u'Successor')
                           .successor_from(predecessor)
                           .having(task_type='report',
                                   issuer=TEST_USER_ID,
                                   responsible=TEST_USER_ID))

        browser.login().open(predecessor, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            ['Successor ({})'.format(self.user.label())],
            browser.css("#successor_tasksBox div.task").text)
        self.assertSequenceEqual(
            [], browser.css("predecessor_taskBox div.task").text)

        browser.login().open(successor, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            ['Predecessor ({})'.format(self.user.label())],
            browser.css("#predecessor_taskBox div.task").text)
        self.assertSequenceEqual(
            [], browser.css("#successor_tasksBox div.task").text)

    # XXX: Not sure if that behavior is really a use case
    # has to be defined after the inbox and forwarding rework

    # @browsing
    # def test_issuer_is_prefixed_by_predecessor_org_unit_on_a_forwarding_successor(self, browser):
    #     create(Builder('org_unit')
    #            .id('client2')
    #            .having(title="Client 2")
    #            .assign_users([self.user]))

    #     forwarding = create(Builder('forwarding').having(issuer=TEST_USER_ID))
    #     successor = create(Builder('task')
    #                        .having(issuer=TEST_USER_ID,
    #                                responsible_client='client2')
    #                        .successor_from(forwarding))

    #     browser.login().open(successor, view='tabbedview_view-overview')

    #     self.assertEquals(
    #         'Client2 / test_user_1_ (test_user_1_)',
    #         browser.css('.issuer').first.text)
