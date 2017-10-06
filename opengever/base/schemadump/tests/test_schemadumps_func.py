from ftw.builder import Builder
from ftw.builder import create
from ftw.bumblebee.tests.helpers import asset as bumblebee_asset
from opengever.base.archeologist import Archeologist
from opengever.testing import FunctionalTestCase
from opengever.testing.helpers import create_document_version
from plone import api
from zope.annotation.interfaces import IAnnotations
import transaction


TEST_ANNOTATION_KEY = 'test_archeologist'


class TestArcheologist(FunctionalTestCase):

    def test_archeologist_returns_modifyable_persistent_reference(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier)
                          .attach_file_containing(
                              bumblebee_asset('example.docx').bytes(),
                              u'example.docx'))
        create_document_version(document, version_id=1)
        create_document_version(document, version_id=2)

        repository = api.portal.get_tool('portal_repository')

        archived_obj = Archeologist(
            document, repository.retrieve(document, selector=1)).excavate()
        annotations = IAnnotations(archived_obj)
        self.assertNotIn(TEST_ANNOTATION_KEY, annotations)
        annotations[TEST_ANNOTATION_KEY] = 'can touch this!'
        archived_obj.some_attr = 'can touch this!'

        transaction.commit()

        archived_obj = Archeologist(
            document, repository.retrieve(document, selector=1)).excavate()
        annotations = IAnnotations(archived_obj)
        self.assertIn(TEST_ANNOTATION_KEY, annotations)
        self.assertEqual('can touch this!', annotations[TEST_ANNOTATION_KEY])
        self.assertEqual('can touch this!', archived_obj.some_attr)
