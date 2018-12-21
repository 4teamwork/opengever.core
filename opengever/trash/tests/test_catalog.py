from opengever.testing import IntegrationTestCase
from plone import api


class TestCatalog(IntegrationTestCase):

    def test_trashed_index_registered(self):
        self.assertIn('trashed', api.portal.get_tool('portal_catalog').indexes())
