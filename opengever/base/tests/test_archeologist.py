from opengever.base.archeologist import Archeologist
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import create_document_version
from plone import api
from zope.annotation.interfaces import IAnnotations


TEST_ANNOTATION_KEY = 'test_archeologist'


class TestArcheologist(IntegrationTestCase):

    def test_archeologist_returns_modifyable_persistent_reference(self):
        self.login(self.regular_user)

        create_document_version(self.document, version_id=1)
        create_document_version(self.document, version_id=2)

        repository = api.portal.get_tool('portal_repository')

        archived_obj = Archeologist(
            self.document, repository.retrieve(self.document, selector=1)).excavate()
        annotations = IAnnotations(archived_obj)
        self.assertNotIn(TEST_ANNOTATION_KEY, annotations)
        annotations[TEST_ANNOTATION_KEY] = 'can touch this!'
        archived_obj.some_attr = 'can touch this!'

        archived_obj = Archeologist(
            self.document, repository.retrieve(self.document, selector=1)).excavate()
        annotations = IAnnotations(archived_obj)
        self.assertIn(TEST_ANNOTATION_KEY, annotations)
        self.assertEqual('can touch this!', annotations[TEST_ANNOTATION_KEY])
        self.assertEqual('can touch this!', archived_obj.some_attr)
