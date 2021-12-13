from opengever.kub.testing import KuBIntegrationTestCase
from opengever.kub.testing import KUB_RESPONSES
from opengever.kub.entity import KuBEntity
import requests_mock


@requests_mock.Mocker()
class TestKuBEntity(KuBIntegrationTestCase):

    def test_data_contains_kub_response(self, mocker):
        url = self.mock_get_by_id(mocker, self.person_jean)
        entity = KuBEntity(self.person_jean)
        self.assertDictEqual(KUB_RESPONSES[url][0], entity.data)

    def test_full_entity_data(self, mocker):
        url = self.mock_get_full_entity_by_id(mocker, self.person_julie)
        entity = KuBEntity(self.person_julie, full=True)
        self.assertDictEqual(KUB_RESPONSES[url], entity.data)

    def test_proxies_getitem_to_data(self, mocker):
        url = self.mock_get_by_id(mocker, self.person_jean)
        entity = KuBEntity(self.person_jean)
        for key, value in KUB_RESPONSES[url][0].items():
            self.assertEqual(value, entity[key])

    def test_serialization_returns_kub_data(self, mocker):
        url = self.mock_get_full_entity_by_id(mocker, self.person_julie)
        entity = KuBEntity(self.person_julie, full=True)
        self.assertDictEqual(KUB_RESPONSES[url], entity.serialize())

    def test_person_entity(self, mocker):
        self.mock_get_by_id(mocker, self.person_jean)
        entity = KuBEntity(self.person_jean)
        self.assertTrue(entity.is_person())
        self.assertFalse(entity.is_organization())
        self.assertFalse(entity.is_membership())

    def test_organization_entity(self, mocker):
        self.mock_get_by_id(mocker, self.org_ftw)
        entity = KuBEntity(self.org_ftw)
        self.assertFalse(entity.is_person())
        self.assertTrue(entity.is_organization())
        self.assertFalse(entity.is_membership())

    def test_membership_entity(self, mocker):
        self.mock_get_by_id(mocker, self.memb_jean_ftw)
        entity = KuBEntity(self.memb_jean_ftw)
        self.assertFalse(entity.is_person())
        self.assertFalse(entity.is_organization())
        self.assertTrue(entity.is_membership())
