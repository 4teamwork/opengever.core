from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from opengever.tabbedview.browser.base_tabs import BaseListingTab
from opengever.tabbedview.sqlsource import SqlTableSource
from opengever.meeting.model import Membership


class DummySQLTableSourceConfig(BaseListingTab):
    """
    """
    sort_on = "member_id"

    def __init__(self, context, request, sql_indexes=None):
        super(DummySQLTableSourceConfig, self).__init__(context, request)

        if sql_indexes:
            # We can set sqlalchemy sort indexes dynamically in tests.
            self.sqlalchemy_sort_indexes = sql_indexes

    def get_base_query(self):
        return Membership.query


class TestSQLAlchemySortIndexes(FunctionalTestCase):

    def test_use_default_sort_index_if_no_sqlalchemy_sort_index_mapping_exists(self):
        config = DummySQLTableSourceConfig(self.portal, self.request)
        source = SqlTableSource(config, self.request)
        self.assertIn('ORDER BY member_id',
                      str(source.build_query()))

    def test_use_sqlalchemy_sort_index_if_mapping_exists(self):
        config = DummySQLTableSourceConfig(self.portal,
                                           self.request,
                                           sql_indexes={'member_id': Membership.member_id})
        source = SqlTableSource(config, self.request)

        self.assertIn('ORDER BY memberships.member_id',
                      str(source.build_query()))


class TestTextFilter(FunctionalTestCase):

    def setUp(self):
        super(TestTextFilter, self).setUp()

        self.dossier = create(Builder('dossier'))
        self.task1 = create(Builder('task')
                            .within(self.dossier)
                            .having(text=u'\xfcberpr\xfcfung')
                            .titled('Task A'))
        self.task2 = create(Builder('task')
                            .within(self.dossier)
                            .titled('Closed Task B'))
        self.task3 = create(Builder('task')
                            .within(self.dossier)
                            .titled('Task C'))

    @browsing
    def test_filtering_on_title(self, browser):
        browser.login().open(
            self.dossier, view='tabbedview_view-tasks',
            data={'searchable_text': 'Task'})

        table = browser.css('.listing').first
        self.assertEquals(['Task A', 'Closed Task B', 'Task C'],
                          [row.get('Title') for row in table.dicts()])

    @browsing
    def test_filtering_on_title_with_multiple_terms(self, browser):
        browser.login().open(
            self.dossier, view='tabbedview_view-tasks',
            data={'searchable_text': 'Task Closed'})

        table = browser.css('.listing').first
        self.assertEquals(['Closed Task B'],
                          [row.get('Title') for row in table.dicts()])

    @browsing
    def test_filtering_on_text(self, browser):
        browser.login().open(
            self.dossier, view='tabbedview_view-tasks',
            data={'searchable_text': u'\xfcberp'})

        table = browser.css('.listing').first
        self.assertEquals(['Task A'],
                          [row.get('Title') for row in table.dicts()])

    @browsing
    def test_filtering_is_case_insensitive(self, browser):
        browser.login().open(
            self.dossier, view='tabbedview_view-tasks',
            data={'searchable_text': u'closed'})

        table = browser.css('.listing').first
        self.assertEquals(['Closed Task B'],
                          [row.get('Title') for row in table.dicts()])

    @browsing
    def test_filtering_on_integer_columns(self, browser):
        browser.login().open(
            self.dossier, view='tabbedview_view-tasks',
            data={'searchable_text': '3'})

        table = browser.css('.listing').first
        self.assertEquals(['Task C'],
                          [row.get('Title') for row in table.dicts()])

    @browsing
    def test_filtering_on_multiple_attributes(self, browser):
        browser.login().open(
            self.dossier, view='tabbedview_view-tasks',
            data={'searchable_text': 'Task 3'})

        table = browser.css('.listing').first
        self.assertEquals(['Task C'],
                          [row.get('Title') for row in table.dicts()])
