from opengever.core.testing import OPENGEVER_FUNCTIONAL_FILING_LAYER
from opengever.testing import FunctionalTestCase
from plone import api


class TestCatalog(FunctionalTestCase):

    def setUp(self):
        super(TestCatalog, self).setUp()
        self.catalog = api.portal.get_tool('portal_catalog')

    def test_is_subdossier_index_registered(self):
        self.assertIn('is_subdossier', self.catalog.indexes())

    def test_containing_subdossier_index_registered(self):
        self.assertIn('containing_subdossier', self.catalog.indexes())

    def test_containing_dossier_index_registered(self):
        self.assertIn('containing_dossier', self.catalog.indexes())


class TestFilingCatalog(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_FILING_LAYER

    def setUp(self):
        super(TestFilingCatalog, self).setUp()
        self.catalog = api.portal.get_tool('portal_catalog')

    def test_filing_no_index_registered(self):
        self.assertIn('filing_no', self.catalog.indexes())

    def test_searchable_filing_no_index_registered(self):
        self.assertIn('searchable_filing_no', self.catalog.indexes())
