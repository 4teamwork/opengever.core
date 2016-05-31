from DateTime import DateTime
from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from lxml.etree import tostring
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.testing import FunctionalTestCase


class TestOverview(FunctionalTestCase):

    use_browser = True

    def setUp(self):
        super(TestOverview, self).setUp()

        self.hugo = create(Builder('fixture').with_hugo_boss())
        self._setup_dossier()

    def _setup_dossier(self):
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
    def test_task_box_items_are_filtered_by_pending_state(self, browser):
        create(Builder('task')
               .within(self.dossier)
               .in_state('task-state-open')
               .titled(u'Task open'))
        create(Builder('task')
               .within(self.dossier)
               .in_state('task-state-tested-and-closed')
               .titled(u'Task closed'))

        browser.login().open(self.dossier, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            browser.css('#newest_tasksBox li:not(.moreLink) a').text,
            ['Task open'])

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
    def test_documents_in_overview_are_linked(self, browser):
        document = create(Builder('document')
                          .within(self.dossier)
                          .titled(u'Document 1'))

        browser.login().open(self.dossier, view='tabbedview_view-overview')

        items = browser.css('#newest_documentsBox li:not(.moreLink) a')

        self.assertEqual(1, len(items))
        self.assertEqual(document.absolute_url(), items.first.get('href'))

    @browsing
    def test_task_link_is_safe_html_transformed(self, browser):
        create(Builder('task')
               .within(self.dossier)
               .titled("Foo <script>alert('foo')</script>"))

        browser.login().open(self.dossier, view='tabbedview_view-overview')

        self.assertEquals(
            [],
            browser.css('span.contenttype-opengever-task-task script'))

        node = browser.css('span.contenttype-opengever-task-task').first
        self.assertEquals(
            '<span class="contenttype-opengever-task-task">Foo &lt;script&gt;alert(\'foo\')&lt;/script&gt;</span>',
            tostring(node.node))

    @browsing
    def test_references_box_lists_regular_references(self, browser):
        browser.login().open(
            self.portal, view='++add++opengever.dossier.businesscasedossier')
        browser.fill({'Title': 'Dossier B', 'Related Dossier': [self.dossier]})
        browser.find('Save').click()
        dossier_b = browser.context

        browser.open(browser.context, view='tabbedview_view-overview')
        references = browser.css('#referencesBox a')
        self.assertEquals(['Testdossier'], references.text)
        self.assertEquals([self.dossier.absolute_url()],
                          [link.get('href') for link in references])


    @browsing
    def test_references_box_lists_back_references(self, browser):
        browser.login().open(
            self.portal, view='++add++opengever.dossier.businesscasedossier')
        browser.fill({'Title': 'Dossier B', 'Related Dossier': [self.dossier]})
        browser.find('Save').click()
        dossier_b = browser.context

        browser.open(self.dossier, view='tabbedview_view-overview')
        references = browser.css('#referencesBox a')
        self.assertEquals(['Dossier B'], references.text)
        self.assertEquals([dossier_b.absolute_url()],
                          [link.get('href') for link in references])


class TestBumblebeeOverview(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    @browsing
    def test_documents_in_overview_are_linked_to_the_overlay(self, browser):
        dossier = create(Builder('dossier')
                         .titled(u'Testdossier')
                         .having(description=u'Hie hesch e beschribig',
                                 responsible='hugo.boss'))

        document = create(Builder('document')
                          .within(dossier)
                          .titled(u'Document 1')
                          .with_dummy_content())

        browser.login().open(dossier, view='tabbedview_view-overview')

        items = browser.css('#newest_documentsBox li:not(.moreLink) a')

        self.assertEqual(1, len(items))
        self.assertEqual(
            '{}/@@bumblebee-overlay-listing'.format(document.absolute_url()),
            items.first.get('data-showroom-target'))
