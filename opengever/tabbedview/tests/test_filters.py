from ftw.solr.query import escape
from ftw.testbrowser import browsing
from opengever.dossier.behaviors.dossier import IDossier
from opengever.tabbedview.filters import CatalogQueryFilter
from opengever.tabbedview.filters import Filter
from opengever.tabbedview.filters import FilterList
from opengever.tabbedview.filters import SubjectFilter
from opengever.testing import IntegrationTestCase
from plone import api
from Products.CMFPlone.utils import safe_unicode
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


class TestSubjectFilter(IntegrationTestCase):

    features = ('solr', )

    def solr_response(self, *facets):
        solr_facets = []
        for facet in facets:
            solr_facets.extend([safe_unicode(facet), 1])

        return {u'facet_counts': {u'facet_fields': {u'Subject': solr_facets}}}

    def test_update_query_does_nothing_if_there_are_no_subjects_defined(self):
        self.assertEqual({}, SubjectFilter(
            self.portal, self.request).update_query({}))

    def test_update_query_uses_subject_values_within_request(self):
        self.login(self.administrator)
        with self.mock_solr(response_json=self.solr_response(u'Vertr\xe4ge')):
            subject_filter = SubjectFilter(self.portal, self.request)

            self.request.form['subjects'] = subject_filter._make_token('Vertr\xc3\xa4ge')
            query = subject_filter.update_query({})

            self.assertEqual((u'Vertr\xe4ge',), query.get('Subject').get('query'))

    def test_update_query_respects_multiple_values(self):
        self.login(self.administrator)
        with self.mock_solr(response_json=self.solr_response('Alpha', 'Beta', 'Gamma')):
            subject_filter = SubjectFilter(self.portal, self.request)

            IDossier(self.dossier).keywords = ('Alpha', 'Beta', 'Gamma')
            self.dossier.reindexObject(idxs=['keywords'])

            subjects = subject_filter.separator.join(['Alpha', 'Beta'])
            self.request.form['subjects'] = subjects

            query = SubjectFilter(self.portal, self.request).update_query({})
            self.assertEqual(
                ('Alpha', 'Beta'),
                query.get('Subject').get('query'))

    def test_multiple_subjects_are_queried_with_AND(self):
        self.login(self.administrator)
        with self.mock_solr(response_json=self.solr_response('Alpha', 'Beta', 'Gamma')):
            subject_filter = SubjectFilter(self.portal, self.request)

            IDossier(self.dossier).keywords = ('Alpha', 'Beta', 'Gamma')
            self.dossier.reindexObject(idxs=['keywords'])

            IDossier(self.meeting_dossier).keywords = ('Alpha', )
            self.meeting_dossier.reindexObject(idxs=['keywords'])

            subjects = subject_filter.separator.join(['Alpha', 'Gamma'])
            self.request.form['subjects'] = subjects

            brains = api.portal.get_tool('portal_catalog')(
                SubjectFilter(self.portal, self.request).update_query({}))

            self.assertEqual(
                [self.dossier],
                [brain.getObject() for brain in brains])

    @browsing
    def test_widget_returns_the_keywordwidget_html(self, browser):
        with self.mock_solr(response_json=self.solr_response()):
            browser.open_html(SubjectFilter(self.portal, self.request).render_widget())

            self.assertEqual(1, len(browser.css('.keyword-widget')))

    @browsing
    def test_subjects_within_request_are_preselected(self, browser):
        self.login(self.administrator)
        with self.mock_solr(response_json=self.solr_response('Alpha')):
            IDossier(self.dossier).keywords = ('Alpha', )
            self.dossier.reindexObject(idxs=['keywords'])

            self.request.form['subjects'] = 'Alpha'

            browser.open_html(SubjectFilter(self.portal, self.request).render_widget())
            self.assertEqual(
                ['Alpha'],
                browser.css('option[selected="selected"]').text)

    @browsing
    def test_restrict_subjects_to_context_children(self, browser):
        """Because we do not test against a real solr instance, we can only
        check the required parameter and filters for a restricted search.
        """
        self.login(self.administrator)

        subject_filter = SubjectFilter(self.dossier, self.request)

        self.assertEqual(
            1, subject_filter._solr_params().get('facet.mincount'),
            "The facet.mincount should be 1. Otherwise, it will return all "
            "Subjects from all objects. But we only want the subjects of the "
            "filtered objects.")

        path_filter = None
        for filter_ in subject_filter._solr_filters():
            if filter_.startswith('path:'):
                path_filter = filter_

        self.assertEqual(
            'path:\\/plone\\/ordnungssystem\\/fuhrung\\/vertrage\\-und\\-vereinbarungen\\/dossier\\-1\\/*',
            path_filter)
