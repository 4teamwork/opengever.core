from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
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
            'filename', 'filesize', 'mimetype', 'creator']
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
             'creator': u'robert.ziegler',
             'description': u'Wichtige Vertr\xe4ge',
             'filename': u'Vertraegsentwurf.docx',
             'filesize': 27413,
             'mimetype': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
             'is_leafnode': None,
             'review_state': u'document-state-draft',
             'title': u'Vertr\xe4gsentwurf'},
            serilized_doc)

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
            'filename', 'filesize', 'mimetype', 'creator']
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
             'creator': u'robert.ziegler',
             'description': u'',
             'filename': u'Die Buergschaft.eml',
             'filesize': 1108,
             'mimetype': u'text/plain',
             'is_leafnode': None,
             'review_state': u'mail-state-active',
             'title': u'Die B\xfcrgschaft'},
            serilized_doc)
