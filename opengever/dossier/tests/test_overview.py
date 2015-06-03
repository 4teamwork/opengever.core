from datetime import date
from DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestOverview(FunctionalTestCase):

    use_browser = True

    def setUp(self):
        super(TestOverview, self).setUp()

        self.hugo = create(Builder('fixture').with_hugo_boss())
        self.dossier = create(Builder('dossier')
                              .titled(u'Testdossier')
                              .having(description=u'Hie hesch e beschribig',
                                      responsible='hugo.boss'))

    @browsing
    def test_description_box_is_displayed(self, browser):
        browser.login().open(self.dossier, view='tabbedview_view-overview')
        self.assertEqual(u'Hie hesch e beschribig',
                         browser.css('#descriptionBox span').first.text)

    @browsing
    def test_task_box_items_are_limited_to_five_and_sorted_by_modified(self, browser):
        for i in range(1, 6):
            create(Builder('task')
                   .within(self.dossier)
                    .with_modification_date(DateTime(2010, 1, 1) + i)
                   .titled(u'Task %s' % i))
        create(Builder('task')
               .within(self.dossier)
                .with_modification_date(DateTime(2009, 12, 1))
               .titled(u'Task 6'))

        browser.login().open(self.dossier, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            browser.css('#newest_tasksBox li:not(.moreLink) a').text,
            ['Task 5', 'Task 4', 'Task 3', 'Task 2', 'Task 1'])

    @browsing
    def test_task_box_items_are_filtered_by_admin_unit(self, browser):
        create(Builder('globalindex_task').having(
            int_id=12345, admin_unit_id='foo', issuing_org_unit='foo',
            sequence_number=4, assigned_org_unit='bar',
            modified=date(2011, 1, 1)))
        create(Builder('task')
               .within(self.dossier)
               .with_modification_date(DateTime(2009, 12, 1))
               .titled(u'Task x'))

        browser.login().open(self.dossier, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            browser.css('#newest_tasksBox li:not(.moreLink) a').text,
            ['Task x'])

    @browsing
    def test_participant_labels_are_displayed(self, browser):
        browser.login().open(self.dossier, view='tabbedview_view-overview')
        self.assertEqual(
            [self.hugo.label()],
            browser.css('#participantsBox li:not(.moreLink) a').text)

    @browsing
    def test_document_box_items_are_limited_to_ten_and_sorted_by_modified(self, browser):
        for i in range(1, 11):
            create(Builder('document')
                   .within(self.dossier)
                   .with_modification_date(DateTime(2010, 1, 1) + i)
                   .titled(u'Document %s' % i))
        create(Builder('document')
               .within(self.dossier)
               .with_modification_date(DateTime(2009, 12, 8))
               .titled(u'Document 11'))

        browser.login().open(self.dossier, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            browser.css('#newest_documentsBox li:not(.moreLink) a').text,
            ['Document 10', 'Document 9', 'Document 8', 'Document 7',
             'Document 6', 'Document 5', 'Document 4', 'Document 3',
             'Document 2', 'Document 1'])

    @browsing
    def test_task_link_is_safe_html_transformed(self, browser):
        create(Builder('task')
               .within(self.dossier)
               .titled("Foo <script>alert('foo')</script>"))

        browser.login().open(self.dossier, view='tabbedview_view-overview')

        self.assertEquals(
            [],
            browser.css('span.contenttype-opengever-task-task script'))

        self.assertEquals(
            ['Foo'],
            browser.css('span.contenttype-opengever-task-task').text)
