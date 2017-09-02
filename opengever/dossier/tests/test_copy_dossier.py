from ftw.builder import Builder
from ftw.builder import create
from opengever.base.interfaces import IReferenceNumberPrefix
from opengever.testing import IntegrationTestCase
from plone import api
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility


class TestCopyDossiers(IntegrationTestCase):

    def test_copying_dossier_purges_child_reference_number_mappings(self):
        self.login(self.dossier_responsible)
        subdossier = create(Builder('dossier').within(self.empty_dossier))

        dossier_copy = api.content.copy(
            source=self.empty_dossier, target=self.empty_repofolder)

        # subdossier is copied
        self.assertEqual(1, len(dossier_copy.get_subdossiers()))
        subdossier_copy = dossier_copy.get_subdossiers()[0].getObject()

        # copied dossier contains mappings for copied subdossiers starting at
        # 1, the mapping was purged on copy
        ref = IReferenceNumberPrefix(dossier_copy)
        self.assertItemsEqual(
            [u'1'],
            ref.get_child_mapping(subdossier_copy).keys())

        # there are no more entries for the previous subdossiers
        intids = getUtility(IIntIds)
        prefixed_intids = ref.get_prefix_mapping(subdossier_copy).keys()
        self.assertNotIn(intids.getId(subdossier), prefixed_intids)
        self.assertIn(intids.getId(subdossier_copy), prefixed_intids)
