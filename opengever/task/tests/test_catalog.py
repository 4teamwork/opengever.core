from opengever.testing import FunctionalTestCase
from plone import api


class TestCatalog(FunctionalTestCase):

    def setUp(self):
        super(TestCatalog, self).setUp()
        self.catalog = api.portal.get_tool('portal_catalog')

    def test_responsible_index_registered(self):
        self.assertIn('responsible', self.catalog.indexes())

    def test_task_type_index_registered(self):
        self.assertIn('task_type', self.catalog.indexes())

    def test_sequence_number_index_registered(self):
        self.assertIn('sequence_number', self.catalog.indexes())

    def test_is_subtask_index_registered(self):
        self.assertIn('is_subtask', self.catalog.indexes())
