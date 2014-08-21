from opengever.core.testing import OPENGEVER_FUNCTIONAL_TESTING
from opengever.dossier.filing.testing import activate_filing_number
from opengever.dossier.filing.testing import inactivate_filing_number
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import PloneSandboxLayer


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


class FilingLayer(PloneSandboxLayer):

    defaultBases = (OPENGEVER_FUNCTIONAL_TESTING,)

    def setUpPloneSite(self, portal):
        activate_filing_number(portal)

    def tearDownPloneSite(self, portal):
        inactivate_filing_number(portal)

OPENGEVER_FILING_LAYER = FilingLayer()


class TestFilingCatalog(FunctionalTestCase):

    layer = OPENGEVER_FILING_LAYER

    def setUp(self):
        super(TestFilingCatalog, self).setUp()
        self.catalog = api.portal.get_tool('portal_catalog')

    def test_filing_no_index_registered(self):
        self.assertIn('filing_no', self.catalog.indexes())

    def test_searchable_filing_no_index_registered(self):
        self.assertIn('searchable_filing_no', self.catalog.indexes())
