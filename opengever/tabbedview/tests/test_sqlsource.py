from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.model import create_session
from opengever.globalindex.model.task import Task
from opengever.meeting.model import Member
from opengever.meeting.model import Membership
from opengever.tabbedview.browser.base_tabs import BaseListingTab
from opengever.tabbedview.sqlsource import cast_to_string
from opengever.tabbedview.sqlsource import SqlTableSource
from opengever.testing import FunctionalTestCase
from opengever.testing import MEMORY_DB_LAYER
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.elements import Cast
from unittest import TestCase


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


class TestCastToString(TestCase):

    layer = MEMORY_DB_LAYER

    def test_does_not_cast_string_fields(self):
        field = Task.title
        self.assertEquals(field, cast_to_string(field))

    def test_cast_integer_fields(self):
        field = Task.sequence_number
        self.assertIsInstance(cast_to_string(field), Cast)
        self.assertIsInstance(cast_to_string(field).type, String)

    def test_does_cast_integer_fields_on_oracle_backends(self):
        original_dialect = create_session().connection().dialect.name
        failed = False

        try:
            create_session().connection().dialect.name = 'oracle'
            field = Task.sequence_number
            self.assertIsInstance(cast_to_string(field), InstrumentedAttribute)
            self.assertIsInstance(cast_to_string(field).type, Integer)
        except BaseException:
            failed = True
        finally:
            create_session().connection().dialect.name = original_dialect

        self.assertFalse(failed, 'Something went wrong when changing the dialect.')


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

    def test_no_sorting_if_column_does_not_exist(self):
        config = DummySQLTableSourceConfig(
            self.portal,
            self.request,
            sql_indexes={'member_id': Membership.member_id})
        config.sort_on = 'this_column_does_not_exist'
        source = SqlTableSource(config, self.request)

        query = source.build_query()
        sorted_query = source.extend_query_with_ordering(query)

        self.assertNotIn(
            'ORDER BY this_column_does_not_exist',
            str(sorted_query))

    def test_allow_special_order_by_in_additional_sql_indices(self):
        config = DummySQLTableSourceConfig(
            self.portal,
            self.request,
            sql_indexes={'member_id': Member.fullname})
        config.sort_on = 'member_id'
        source = SqlTableSource(config, self.request)

        query = source.build_query()
        sorted_query = source.extend_query_with_ordering(query)

        # fullname is  a col-property it will order by lastname and firstname.
        # only assert against lastname as the rest of the query serializes
        # in a weird way here
        self.assertIn(
            'ORDER BY members.lastname',
            str(sorted_query))


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
