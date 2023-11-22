from ftw.testbrowser import browsing
from opengever.base.oguid import Oguid
from opengever.dossier.behaviors.dossier import IDossier
from opengever.locking.lock import COPIED_TO_WORKSPACE_LOCK
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import MockDossierTypes
from plone.locking.interfaces import ILockable
from plone.restapi.interfaces import ISerializeToJsonSummary
from zope.component import getMultiAdapter


class TestGeverSummarySerializer(IntegrationTestCase):

    @browsing
    def test_document_summary_supports_filename_filesize_and_mimetype_as_metadata_fields(self, browser):
        self.login(self.regular_user, browser)

        serializer = getMultiAdapter(
            (self.document, self.request),
            ISerializeToJsonSummary)
        serilized_doc = serializer()

        self.assertNotIn('filename', serilized_doc)
        self.assertNotIn('filesize', serilized_doc)
        self.assertNotIn('mimetype', serilized_doc)
        self.assertNotIn('creator', serilized_doc)

        self.request.form['metadata_fields'] = [
            'filename', 'filesize', 'mimetype', 'creator', 'oguid']
        serializer = getMultiAdapter(
            (self.document, self.request),
            ISerializeToJsonSummary)
        serilized_doc = serializer()

        self.assertIn('filename', serilized_doc)
        self.assertIn('filesize', serilized_doc)
        self.assertIn('mimetype', serilized_doc)
        self.assertIn('creator', serilized_doc)

        self.assertDictEqual(
            {'@id': self.document.absolute_url(),
             '@type': u'opengever.document.document',
             'UID': u'createtreatydossiers000000000002',
             'checked_out': None,
             'creator': u'robert.ziegler',
             'description': u'Wichtige Vertr\xe4ge',
             'file_extension': u'.docx',
             'filename': u'Vertraegsentwurf.docx',
             'filesize': 27413,
             'mimetype': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
             'oguid': Oguid.for_object(self.document).id,
             'is_leafnode': None,
             'review_state': u'document-state-draft',
             'title': u'Vertr\xe4gsentwurf'},
            serilized_doc)

    @browsing
    def test_document_summary_includes_is_locked_by_copy_to_workspace_as_metadata_fields(self, browser):
        self.activate_feature('workspace_client')
        self.login(self.regular_user, browser)
        ILockable(self.document).lock(COPIED_TO_WORKSPACE_LOCK)

        serializer = getMultiAdapter(
            (self.document, self.request),
            ISerializeToJsonSummary)
        serialized_doc = serializer()
        self.assertTrue(serialized_doc.get('is_locked_by_copy_to_workspace'))

    @browsing
    def test_mail_summary_supports_filename_filesize_and_mimetype_as_metadata_fields(self, browser):
        self.login(self.regular_user, browser)

        serializer = getMultiAdapter(
            (self.mail_eml, self.request),
            ISerializeToJsonSummary)
        serilized_doc = serializer()

        self.assertNotIn('filename', serilized_doc)
        self.assertNotIn('filesize', serilized_doc)
        self.assertNotIn('mimetype', serilized_doc)
        self.assertNotIn('creator', serilized_doc)

        self.request.form['metadata_fields'] = [
            'filename', 'filesize', 'mimetype', 'creator', 'oguid']
        serializer = getMultiAdapter(
            (self.mail_eml, self.request),
            ISerializeToJsonSummary)
        serilized_doc = serializer()

        self.assertIn('filename', serilized_doc)
        self.assertIn('filesize', serilized_doc)
        self.assertIn('mimetype', serilized_doc)
        self.assertIn('creator', serilized_doc)

        self.assertDictEqual(
            {'@id': self.mail_eml.absolute_url(),
             '@type': u'ftw.mail.mail',
             'UID': u'createemails00000000000000000001',
             'checked_out': None,
             'creator': u'robert.ziegler',
             'description': u'',
             'file_extension': u'.eml',
             'filename': u'Die Buergschaft.eml',
             'filesize': 1108,
             'mimetype': u'text/plain',
             'oguid': Oguid.for_object(self.mail_eml).id,
             'is_leafnode': None,
             'review_state': u'mail-state-active',
             'title': u'Die B\xfcrgschaft'},
            serilized_doc)

    @browsing
    def test_mail_summary_includes_is_locked_by_copy_to_workspace_as_metadata_fields(self, browser):
        self.activate_feature('workspace_client')
        self.login(self.regular_user, browser)
        ILockable(self.mail_eml).lock(COPIED_TO_WORKSPACE_LOCK)

        serializer = getMultiAdapter(
            (self.mail_eml, self.request),
            ISerializeToJsonSummary)
        serialized_doc = serializer()
        self.assertTrue(serialized_doc.get('is_locked_by_copy_to_workspace'))

    @browsing
    def test_dossier_summary_includes_dossier_type(self, browser):
        self.login(self.regular_user, browser)

        MockDossierTypes.install()
        IDossier(self.dossier).dossier_type = 'project'

        serializer = getMultiAdapter(
            (self.dossier, self.request),
            ISerializeToJsonSummary)

        serialized_dossier = serializer()
        self.assertEqual('project', serialized_dossier['dossier_type'])
