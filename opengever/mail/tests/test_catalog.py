from opengever.testing import FunctionalTestCase
from plone import api


class TestCatalog(FunctionalTestCase):

    def setUp(self):
        super(TestCatalog, self).setUp()
        self.catalog = api.portal.get_tool('portal_catalog')

    def test_sortable_author_index_registered(self):
        self.assertIn('sortable_author', self.catalog.indexes())
