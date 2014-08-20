from opengever.testing import FunctionalTestCase
from plone import api


class TestCatalog(FunctionalTestCase):

    def setUp(self):
        super(TestCatalog, self).setUp()
        self.catalog = api.portal.get_tool('portal_catalog')

    def test_contactid_index_registered(self):
        self.assertIn('contactid', self.catalog.indexes())

    def test_firstname_index_registered(self):
        self.assertIn('firstname', self.catalog.indexes())

    def test_lastname_index_registered(self):
        self.assertIn('lastname', self.catalog.indexes())

    def test_email_index_registered(self):
        self.assertIn('email', self.catalog.indexes())

    def test_phone_office_index_registered(self):
        self.assertIn('phone_office', self.catalog.indexes())
