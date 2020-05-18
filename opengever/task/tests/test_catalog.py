from opengever.testing import FunctionalTestCase
from plone import api


class TestCatalog(FunctionalTestCase):

    def setUp(self):
        super(TestCatalog, self).setUp()
        self.catalog = api.portal.get_tool('portal_catalog')

    def test_deadline_index_registered(self):
        self.assertIn('deadline', self.catalog.indexes())

    def test_date_of_completion_index_registered(self):
        self.assertIn('date_of_completion', self.catalog.indexes())

    def test_responsible_index_registered(self):
        self.assertIn('responsible', self.catalog.indexes())

    def test_issuer_index_registered(self):
        self.assertIn('issuer', self.catalog.indexes())

    def test_task_type_index_registered(self):
        self.assertIn('task_type', self.catalog.indexes())

    def test_client_id_index_registered(self):
        self.assertIn('client_id', self.catalog.indexes())

    def test_sequence_number_index_registered(self):
        self.assertIn('sequence_number', self.catalog.indexes())

    def test_is_subtask_index_registered(self):
        self.assertIn('is_subtask', self.catalog.indexes())

    def test_predecessor_index_registered(self):
        self.assertIn('predecessor', self.catalog.indexes())
