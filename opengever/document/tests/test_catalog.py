from opengever.testing import FunctionalTestCase
from plone import api


class TestCatalog(FunctionalTestCase):

    def setUp(self):
        super(TestCatalog, self).setUp()
        self.catalog = api.portal.get_tool('portal_catalog')

    def test_delivery_date_index_registered(self):
        self.assertIn('delivery_date', self.catalog.indexes())

    def test_document_author_index_registered(self):
        self.assertIn('document_author', self.catalog.indexes())

    def test_cchecked_out_index_registered(self):
        self.assertIn('checked_out', self.catalog.indexes())

    def test_document_date_index_registered(self):
        self.assertIn('document_date', self.catalog.indexes())

    def test_receipt_date_index_registered(self):
        self.assertIn('receipt_date', self.catalog.indexes())

    def test_sortable_author_index_registered(self):
        self.assertIn('sortable_author', self.catalog.indexes())

    def test_public_trial_index_registered(self):
        self.assertIn('public_trial', self.catalog.indexes())
