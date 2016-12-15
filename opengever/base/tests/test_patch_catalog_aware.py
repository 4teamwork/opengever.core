from ftw.builder import Builder
from ftw.builder import create
from opengever.base.monkey.patches.cmf_catalog_aware import DeactivatedCatalogIndexing
from opengever.testing import FunctionalTestCase
from plone import api


class TestPatchCMFCatalogAware(FunctionalTestCase):

    def setUp(self):
        super(TestPatchCMFCatalogAware, self).setUp()
        self.catalog = api.portal.get_tool('portal_catalog')
        self.dossier = create(Builder('dossier'))

    def test_do_not_change_catalog_reindexObject_in_normal_usage(self):
        self.dossier.title = "Foo Bar"
        self.dossier.reindexObject()

        brain = self.catalog(UID=self.dossier.UID())[0]

        self.assertEqual('Foo Bar', brain.Title)

    def test_do_not_reindexObject_in_context_manager(self):
        self.dossier.title = "Foo Bar"

        with DeactivatedCatalogIndexing():
            self.dossier.reindexObject()

        brain = self.catalog(UID=self.dossier.UID())[0]

        self.assertEqual('', brain.Title)

    def test_do_not_change_catalog_unindexObject_in_normal_usage(self):
        self.dossier.unindexObject()

        self.assertEqual(0, len(self.catalog(UID=self.dossier.UID())))

    def test_do_not_unindexObject_in_context_manager(self):
        with DeactivatedCatalogIndexing():
            self.dossier.unindexObject()

        self.assertEqual(1, len(self.catalog(UID=self.dossier.UID())))

    def test_do_not_change_catalog_indexObject_in_normal_usage(self):
        self.dossier.unindexObject()

        self.dossier.indexObject()

        self.assertEqual(1, len(self.catalog(UID=self.dossier.UID())))

    def test_do_not_indexObject_in_context_manager(self):
        self.dossier.unindexObject()

        with DeactivatedCatalogIndexing():
            self.dossier.indexObject()

        self.assertEqual(0, len(self.catalog(UID=self.dossier.UID())))
