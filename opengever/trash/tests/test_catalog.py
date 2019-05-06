from datetime import datetime
from ftw.testing import freeze
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import index_data_for
from opengever.trash.trash import Trasher
from plone import api


class TestCatalog(IntegrationTestCase):

    def test_trashed_index_registered(self):
        self.assertIn('trashed', api.portal.get_tool('portal_catalog').indexes())

    def test_modified_index_gets_updated_when_trashing(self):
        self.login(self.regular_user)

        with freeze(datetime(2014, 5, 7, 12, 30)) as clock:
            Trasher(self.subsubdocument).trash()
            clock.forward(minutes=5)

            Trasher(self.taskdocument).trash()
            clock.forward(minutes=5)

            Trasher(self.document).trash()
            clock.forward(minutes=5)

            Trasher(self.subdocument).trash()

        catalog = api.portal.get_tool('portal_catalog')
        modified_idx = catalog._catalog.indexes['modified']

        def modified_idx_value(obj):
            return index_data_for(obj)['modified']

        def to_idx_value(value):
            return modified_idx._convert(value)

        self.assertEqual(
            to_idx_value(datetime(2014, 5, 7, 12, 30)),
            modified_idx_value(self.subsubdocument))

        self.assertEqual(
            to_idx_value(datetime(2014, 5, 7, 12, 35)),
            modified_idx_value(self.taskdocument))

        self.assertEqual(
            to_idx_value(datetime(2014, 5, 7, 12, 40)),
            modified_idx_value(self.document))

        self.assertEqual(
            to_idx_value(datetime(2014, 5, 7, 12, 45)),
            modified_idx_value(self.subdocument))
