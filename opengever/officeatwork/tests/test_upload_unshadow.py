from opengever.testing import IntegrationTestCase
from plone import api
from plone.namedfile.file import NamedBlobFile
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class TestUploadUnshadow(IntegrationTestCase):

    def test_uploading_a_file_to_a_shadow_document_exits_shadow_state(self):
        self.login(self.dossier_responsible)
        self.assertTrue(self.shadow_document.is_shadow_document())
        self.assertEqual('document-state-shadow', api.content.get_state(self.shadow_document))

        self.shadow_document.file = NamedBlobFile(data='New', filename=u'test.txt')
        notify(ObjectModifiedEvent(self.shadow_document))

        self.assertFalse(self.shadow_document.is_shadow_document())
        self.assertEqual('document-state-draft', api.content.get_state(self.shadow_document))

    def test_uploading_a_file_to_a_shadow_document_changes_visibility(self):
        # XXX - Work around the fixture lookup table permissions
        with self.login(self.dossier_responsible):
            shadow_document = self.shadow_document

        self.login(self.regular_user)
        self.assert_has_not_permissions(('View',), shadow_document)

        shadow_document.file = NamedBlobFile(data='New', filename=u'test.txt')
        notify(ObjectModifiedEvent(shadow_document))

        self.assertTrue(shadow_document.file)
        self.assert_has_permissions(('View',), shadow_document)
