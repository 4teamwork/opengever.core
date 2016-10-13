from ftw.builder import Builder
from ftw.builder import create
from opengever.base.interfaces import IReferenceNumberPrefix
from opengever.testing import FunctionalTestCase
from plone import api
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility


class TestCopyDossiers(FunctionalTestCase):

    def setUp(self):
        super(TestCopyDossiers, self).setUp()
        self.request = self.layer['request']

        self.root = create(Builder('repository_root'))
        self.source_repo = create(Builder('repository').within(self.root))
        self.target_repo = create(Builder('repository').within(self.root))

    def test_copying_dossier_purges_child_reference_number_mappings(self):
        dossier = create(Builder('dossier').within(self.source_repo))
        subdossier_1 = create(Builder('dossier').within(dossier))
        subdossier_2 = create(Builder('dossier').within(dossier))

        dossier_copy = api.content.copy(
            source=dossier, target=self.target_repo)

        # there are two copied subdossiers
        self.assertEqual(2, len(dossier_copy.listFolderContents()))
        subdossier1_copy = dossier_copy.listFolderContents()[0]

        # copied dossier contains mappings for copied subdossiers starting at
        # 1, the mapping was purged on copy
        ref = IReferenceNumberPrefix(dossier_copy)
        ref.get_child_mapping(subdossier1_copy)
        self.assertItemsEqual(
            [u'1', u'2'], ref.get_child_mapping(subdossier1_copy).keys())

        # there are no more entries for the previous subdossiers
        intids = getUtility(IIntIds)
        prefixed_intids = ref.get_prefix_mapping(subdossier1_copy).keys()
        self.assertNotIn(intids.getId(subdossier_1), prefixed_intids)
        self.assertNotIn(intids.getId(subdossier_2), prefixed_intids)
