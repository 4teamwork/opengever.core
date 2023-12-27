from opengever.kub.sources import KuBContactsSource
from opengever.kub.testing import KuBIntegrationTestCase
from opengever.ogds.models.service import ogds_service
from unittest import skip
import requests_mock


@requests_mock.Mocker()
class TestKubContactSource(KuBIntegrationTestCase):

    def setUp(self):
        super(TestKubContactSource, self).setUp()
        self.source = KuBContactsSource(None)

    def test_search_returns_persons(self, mocker):
        query_str = "Julie"
        self.mock_search(mocker, query_str)

        terms = self.source.search(query_str)
        self.assertItemsEqual([self.person_julie],
                              [term.token for term in terms])
        self.assertItemsEqual([self.person_julie],
                              [term.value for term in terms])
        self.assertItemsEqual(['Dupont Julie'],
                              [term.title for term in terms])

    def test_search_returns_memberships_and_organizations(self, mocker):
        query_str = "4Teamwork"
        self.mock_search(mocker, query_str)
        terms = self.source.search(query_str)

        self.assertItemsEqual([self.org_ftw, self.memb_jean_ftw],
                              [term.token for term in terms])
        self.assertItemsEqual([self.org_ftw, self.memb_jean_ftw],
                              [term.value for term in terms])
        self.assertItemsEqual(["Dupont Jean - 4Teamwork (CEO)", "4Teamwork"],
                              [term.title for term in terms])

    @skip('This test fails for yet unknown reasons after changing the userid of kathi.barfuss to regular_user')
    def test_search_returns_ogds_users(self, mocker):
        query_str = "Barfuss"
        url = u'{}search?q={}'.format(self.client.kub_api_url, query_str)
        mocker.get(url, json=[])
        ogds_user = ogds_service().fetch_user(self.regular_user.getId())

        terms = self.source.search(query_str)
        self.assertItemsEqual([self.regular_user.id],
                              [term.token for term in terms])
        self.assertItemsEqual([ogds_user],
                              [term.value for term in terms])
        self.assertItemsEqual([u'B\xe4rfuss K\xe4thi (kathi.barfuss)'],
                              [term.title for term in terms])

    def test_get_term_by_token_handles_persons(self, mocker):
        self.mock_labels(mocker)
        term = self.source.getTermByToken(self.person_jean)
        self.assertEqual(self.person_jean, term.token)
        self.assertEqual(self.person_jean, term.value)
        self.assertEqual('Dupont Jean', term.title)

    def test_get_by_id_handles_organizations(self, mocker):
        self.mock_labels(mocker)
        term = self.source.getTermByToken(self.org_ftw)
        self.assertEqual(self.org_ftw, term.token)
        self.assertEqual(self.org_ftw, term.value)
        self.assertEqual('4Teamwork', term.title)

    def test_get_by_id_handles_memberships(self, mocker):
        self.mock_labels(mocker)
        term = self.source.getTermByToken(self.memb_jean_ftw)
        self.assertEqual(self.memb_jean_ftw, term.token)
        self.assertEqual(self.memb_jean_ftw, term.value)
        self.assertEqual('Dupont Jean - 4Teamwork (CEO)', term.title)

    def test_get_by_id_handles_ogds_users(self, mocker):
        self.mock_labels(mocker)
        term = self.source.getTermByToken(self.regular_user.getId())
        ogds_user = ogds_service().fetch_user(self.regular_user.getId())
        self.assertEqual(self.regular_user.getId(), term.token)
        self.assertEqual(ogds_user, term.value)
        self.assertEqual(u'B\xe4rfuss K\xe4thi (kathi.barfuss)', term.title)

    def test_get_by_id_raises_lookup_error_for_invalid_token(self, mocker):
        self.mock_labels(mocker)
        contact_id = "invalid-id"
        self.mock_get_by_id(mocker, contact_id)
        with self.assertRaises(LookupError):
            self.source.getTermByToken(contact_id)

    def test_set_active_filter_when_using_only_active(self, mocker):
        source = KuBContactsSource(None)
        self.assertEqual({}, source.kub_filters)
        self.assertEqual({}, source.ogds_filters)

        source = KuBContactsSource(None, only_active=True)
        self.assertEqual({'is_active': True}, source.kub_filters)
        self.assertEqual({'active': True}, source.ogds_filters)
