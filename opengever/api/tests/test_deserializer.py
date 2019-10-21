from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
import os
from base64 import b64encode
from opengever.testing.assets import path_to_asset


def _base64_str(s):
    if not isinstance(s, bytes):
        s = s.encode("utf-8")
    s = b64encode(s)
    if not isinstance(s, str):
        s = s.decode("utf-8")
    return s


def _prepare_metadata(filename, content_type, _type=None):
    return "filename {},content-type {}{}".format(
        _base64_str(filename), _base64_str(content_type), ', @type ' + _base64_str(_type) if _type else ''
    )


msg_mimetype = u'application/vnd.ms-outlook'
eml_mimetype = u'message/rfc822'
p7m_mimetype = u'application/pkcs7-mime'


class TestRepositoryFolderSerializer(IntegrationTestCase):

    @browsing
    def test_tus_can_upload_text_file_as_ogdocument(self, browser):
        self.login(self.regular_user, browser)

        # initialize the upload with POST
        filename = 'text.txt'
        file_path = path_to_asset(filename)
        file_size = os.path.getsize(file_path)
        metadata = _prepare_metadata(filename, eml_mimetype, 'opengever.document.document')

        response = browser.open(
            self.empty_dossier.absolute_url() + '/@tus-upload',
            method='POST',
            headers={
                'Accept': 'application/json',
                "Tus-Resumable": "1.0.0",
                "Upload-Length": str(file_size),
                "Upload-Metadata": metadata
                },
        )

        self.assertEqual(response.status_code, 201)

        # upload the data with PATCH
        location = response.headers["Location"]
        with self.observe_children(self.empty_dossier) as children:
            with open(file_path, "rb") as infile:
                response = browser.open(
                    location,
                    method='PATCH',
                    headers={
                        'Accept': 'application/json',
                        "Content-Type": "application/offset+octet-stream",
                        "Upload-Offset": "0",
                        "Tus-Resumable": "1.0.0",
                        },
                    data=infile.read(),
                )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(1, len(children['added']))
        uploaded_document = children['added'].pop()
        self.assertEqual(filename, uploaded_document.get_filename())
        self.assertEqual('opengever.document.document', uploaded_document.portal_type)
        self.assertEqual(file_size, uploaded_document.get_file().size)

    @browsing
    def test_tus_can_upload_eml_mail(self, browser):
        self.login(self.regular_user, browser)

        # initialize the upload with POST
        filename = 'mail_with_one_mail_attachment.eml'
        file_path = path_to_asset(filename)
        file_size = os.path.getsize(file_path)
        metadata = _prepare_metadata(filename, eml_mimetype, 'ftw.mail.mail')

        response = browser.open(
            self.empty_dossier.absolute_url() + '/@tus-upload',
            method='POST',
            headers={
                'Accept': 'application/json',
                "Tus-Resumable": "1.0.0",
                "Upload-Length": str(file_size),
                "Upload-Metadata": metadata
                },
        )

        self.assertEqual(response.status_code, 201)

        # upload the data with PATCH
        location = response.headers["Location"]
        with self.observe_children(self.empty_dossier) as children:
            with open(file_path, "rb") as infile:
                response = browser.open(
                    location,
                    method='PATCH',
                    headers={
                        'Accept': 'application/json',
                        "Content-Type": "application/offset+octet-stream",
                        "Upload-Offset": "0",
                        "Tus-Resumable": "1.0.0",
                        },
                    data=infile.read(),
                )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(1, len(children['added']))
        uploaded_mail = children['added'].pop()

        self.assertEqual(u'Aeusseres Testmaeil.eml', uploaded_mail.get_filename())
        self.assertEqual('ftw.mail.mail', uploaded_mail.portal_type)
        self.assertEqual(file_size, uploaded_mail.get_file().size)
        self.assertIsNone(uploaded_mail.original_message)

    @browsing
    def test_tus_can_upload_msg_mail(self, browser):
        self.login(self.regular_user, browser)

        # initialize the upload with POST
        filename = 'testmail.msg'
        file_path = path_to_asset(filename)
        file_size = os.path.getsize(file_path)
        metadata = _prepare_metadata(filename, eml_mimetype, 'ftw.mail.mail')

        response = browser.open(
            self.empty_dossier.absolute_url() + '/@tus-upload',
            method='POST',
            headers={
                'Accept': 'application/json',
                "Tus-Resumable": "1.0.0",
                "Upload-Length": str(file_size),
                "Upload-Metadata": metadata
                },
        )

        self.assertEqual(response.status_code, 201)

        # upload the data with PATCH
        location = response.headers["Location"]
        with self.observe_children(self.empty_dossier) as children:
            with open(file_path, "rb") as infile:
                response = browser.open(
                    location,
                    method='PATCH',
                    headers={
                        'Accept': 'application/json',
                        "Content-Type": "application/offset+octet-stream",
                        "Upload-Offset": "0",
                        "Tus-Resumable": "1.0.0",
                        },
                    data=infile.read(),
                )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(1, len(children['added']))
        uploaded_mail = children['added'].pop()

        self.assertEqual(filename, uploaded_mail.get_filename())
        self.assertEqual('ftw.mail.mail', uploaded_mail.portal_type)
        self.assertEqual(file_size, uploaded_mail.get_file().size)

        # make sure that the uploaded file was moved to the original_message field
        self.assertIsNotNone(uploaded_mail.original_message)
        self.assertEqual(file_size, uploaded_mail.original_message.size)

    @browsing
    def test_tus_can_upload_p7m_mail(self, browser):
        self.login(self.regular_user, browser)

        # initialize the upload with POST
        filename = 'signed.p7m'
        file_path = path_to_asset(filename)
        file_size = os.path.getsize(file_path)
        metadata = _prepare_metadata(filename, p7m_mimetype, 'ftw.mail.mail')

        response = browser.open(
            self.empty_dossier.absolute_url() + '/@tus-upload',
            method='POST',
            headers={
                'Accept': 'application/json',
                "Tus-Resumable": "1.0.0",
                "Upload-Length": str(file_size),
                "Upload-Metadata": metadata
                },
        )

        self.assertEqual(response.status_code, 201)

        # upload the data with PATCH
        location = response.headers["Location"]
        with self.observe_children(self.empty_dossier) as children:
            with open(file_path, "rb") as infile:
                response = browser.open(
                    location,
                    method='PATCH',
                    headers={
                        'Accept': 'application/json',
                        "Content-Type": "application/offset+octet-stream",
                        "Upload-Offset": "0",
                        "Tus-Resumable": "1.0.0",
                        },
                    data=infile.read(),
                )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(1, len(children['added']))
        uploaded_mail = children['added'].pop()

        self.assertEqual(u'Hello.p7m', uploaded_mail.get_filename())
        self.assertEqual('ftw.mail.mail', uploaded_mail.portal_type)
        self.assertEqual(file_size, uploaded_mail.get_file().size)
        self.assertIsNone(uploaded_mail.original_message)
