from opengever.tabbedview.filters import CatalogQueryFilter
from opengever.tabbedview.filters import Filter
from opengever.tabbedview.filters import FilterList
from unittest import TestCase


class TestFilterList(TestCase):

    def setUp(self):
        super(TestFilterList, self).setUp()

        self.filter_all = Filter('filter_all', 'All')
        self.filter_active = CatalogQueryFilter(
            'filter_active', 'Active', default=True,
            query_extension={'review_state': ['state-open']})
        self.filter_closed = CatalogQueryFilter(
            'filter_closed', 'Closed',
            query_extension={'review_state': ['state-closed']})

        self.filter_list = FilterList(
            self.filter_all, self.filter_active, self.filter_closed)

    def test_get_by_filter_id(self):
        self.assertEquals(
            self.filter_all, self.filter_list['filter_all'])

        self.assertEquals(
            self.filter_active, self.filter_list['filter_active'])

    def test_default_filter(self):
        self.assertEquals(self.filter_active, self.filter_list.default_filter)

    def test_only_one_default_filter_possible(self):
        with self.assertRaises(ValueError) as cm:
            FilterList(Filter('all', 'All', default=True),
                       Filter('active', 'Active', default=True))

        self.assertEquals(
            'Only one filter marked as default possible.',
            str(cm.exception))

    def test_filters_are_ordered(self):
        self.assertEquals(
            [self.filter_all, self.filter_active, self.filter_closed],
            self.filter_list.filters())

    def test_is_active_when_id_matchs(self):
        selected_filter_id = 'filter_all'

        self.assertTrue(self.filter_all.is_active(selected_filter_id))
        self.assertFalse(self.filter_active.is_active(selected_filter_id))
        self.assertFalse(self.filter_closed.is_active(selected_filter_id))

    def test_is_active_when_its_the_default_and_currently_no_filter_is_selected(self):
        selected_filter_id = None

        self.assertFalse(self.filter_all.is_active(selected_filter_id))
        self.assertTrue(self.filter_active.is_active(selected_filter_id))
        self.assertFalse(self.filter_closed.is_active(selected_filter_id))

    def test_update_query_by_selected_filter(self):
        selected_filter_id = 'filter_closed'

        self.assertEquals(
            {'review_state': ['state-closed']},
            self.filter_list.update_query({}, selected_filter_id))

    def test_update_query_by_default_filter_when_no_filter_is_selected(self):
        selected_filter_id = None

        self.assertEquals(
            {'review_state': ['state-open']},
            self.filter_list.update_query({}, selected_filter_id))
