from opengever.kub.sources import KuBContactsSource
from opengever.kub.testing import KuBIntegrationTestCase
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

    def test_get_term_by_token_handles_persons(self, mocker):
        self.mock_get_by_id(mocker, self.person_jean)
        term = self.source.getTermByToken(self.person_jean)
        self.assertEqual(self.person_jean, term.token)
        self.assertEqual(self.person_jean, term.value)
        self.assertEqual('Dupont Jean', term.title)

    def test_get_by_id_handles_organizations(self, mocker):
        self.mock_get_by_id(mocker, self.org_ftw)
        term = self.source.getTermByToken(self.org_ftw)
        self.assertEqual(self.org_ftw, term.token)
        self.assertEqual(self.org_ftw, term.value)
        self.assertEqual('4Teamwork', term.title)

    def test_get_by_id_handles_memberships(self, mocker):
        self.mock_get_by_id(mocker, self.memb_jean_ftw)
        term = self.source.getTermByToken(self.memb_jean_ftw)
        self.assertEqual(self.memb_jean_ftw, term.token)
        self.assertEqual(self.memb_jean_ftw, term.value)
        self.assertEqual('Dupont Jean - 4Teamwork (CEO)', term.title)

    def test_get_by_id_raises_lookup_error_for_invalid_token(self, mocker):
        contact_id = "invalid-id"
        self.mock_get_by_id(mocker, contact_id)
        with self.assertRaises(LookupError):
            self.source.getTermByToken(contact_id)