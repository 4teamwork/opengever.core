from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.mail.mail import IOGMail
from opengever.testing import IntegrationTestCase
from opengever.testing.assets import load
from plone.app.uuid.utils import uuidToObject
from plone.namedfile.file import NamedBlobFile
from plone.uuid.interfaces import IUUID
import base64
import json


class TestGetMail(IntegrationTestCase):

    @browsing
    def test_additional_metadata_for_mails(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.mail_eml, headers=self.api_headers)

        self.assertIsNone(browser.json['checked_out'])
        self.assertIsNone(browser.json['checked_out_fullname'])
        self.assertFalse(browser.json['is_locked'])
        self.assertEqual(u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
                         browser.json['containing_dossier'])
        self.assertIsNone(browser.json['containing_subdossier'])
        self.assertFalse(browser.json['trashed'])
        self.assertFalse(browser.json['is_shadow_document'])
        self.assertFalse(0, browser.json['current_version_id'])
        self.assertEqual([], browser.json['attachments'])

    @browsing
    def test_contains_also_original_message(self, browser):
        self.login(self.regular_user, browser)
        IOGMail(self.mail_eml).original_message = NamedBlobFile(
            data='__DATA__', filename=u'testmail.msg')

        browser.open(self.mail_eml.absolute_url(), method='GET',
                     headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        expected_message = {
            u'content-type': u'application/vnd.ms-outlook',
            u'download': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-29'
                         u'/@@download/original_message',
            u'filename': u'testmail.msg',
            u'size': 8,
        }
        self.assertEqual(expected_message, browser.json.get('original_message'))

    @browsing
    def test_mail_serialization_contains_attachments(self, browser):
        self.login(self.regular_user, browser)
        mail = create(Builder('mail')
                      .within(self.dossier)
                      .with_asset_message(
                          'mail_with_multiple_attachments.eml'))
        doc = mail.extract_attachment_into_parent(4)

        browser.open(mail, headers=self.api_headers)
        expected = [
            {u'content-type': u'message/rfc822',
             u'filename': u'Inneres Testma\u0308il ohne Attachments.eml',
             u'position': 2,
             u'size': 930},
            {u'content-type': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
             u'extracted': True,
             u'extracted_document_uid': IUUID(doc),
             u'extracted_document_url': doc.absolute_url(),
             u'filename': u'word_document.docx',
             u'position': 4,
             u'size': 22962},
            {u'content-type': u'text/plain',
             u'filename': u'Text.txt',
             u'position': 5,
             u'size': 26}]
        self.assertEqual(expected, browser.json['attachments'])


class TestCreateMail(IntegrationTestCase):

    @browsing
    def test_create_mail_from_msg_converts_to_eml(self, browser):
        self.login(self.regular_user, browser)
        msg = base64.b64encode(load('testmail.msg'))

        with self.observe_children(self.dossier) as children:
            browser.open(
                self.dossier.absolute_url(),
                data='{"@type": "ftw.mail.mail",'
                     '"message": {"data": "%s", "encoding": "base64", '
                     '"filename": "testmail.msg"}}' % msg,
                method='POST',
                headers=self.api_headers)

        self.assertEqual(browser.status_code, 201)
        self.assertEqual(1, len(children.get('added')))

        mail = children['added'].pop()
        self.assertEqual(mail.Title(), 'testmail')
        self.assertEqual(mail.message.filename, 'testmail.eml')
        self.assertIn('MIME-Version: 1.0', mail.message.data)
        self.assertEqual(mail.original_message.filename, 'testmail.msg')

    @browsing
    def test_create_mail_from_eml(self, browser):
        self.login(self.regular_user, browser)
        msg = base64.b64encode(load('mail_with_one_mail_attachment.eml'))

        with self.observe_children(self.dossier) as children:
            browser.open(
                self.dossier.absolute_url(),
                data='{"@type": "ftw.mail.mail",'
                     '"message": {"data": "%s", "encoding": "base64", '
                     '"filename": "testmail.eml"}}' % msg,
                method='POST',
                headers=self.api_headers)

        self.assertEqual(browser.status_code, 201)
        self.assertEqual(1, len(children.get('added')))

        mail = children['added'].pop()
        self.assertEqual(mail.Title(), '\xc3\x84usseres Testm\xc3\xa4il')
        self.assertEqual(mail.message.filename, 'Aeusseres Testmaeil.eml')
        self.assertEqual(mail.original_message, None)

    @browsing
    def test_create_mail_from_p7m(self, browser):
        self.login(self.regular_user, browser)
        mail_file = base64.b64encode(load('signed.p7m'))

        with self.observe_children(self.dossier) as children:
            browser.open(
                self.dossier.absolute_url(),
                data='{"@type": "ftw.mail.mail",'
                     '"message": {"data": "%s", "encoding": "base64", '
                     '"filename": "signed.p7m"}}' % mail_file,
                method='POST',
                headers=self.api_headers)

        self.assertEqual(browser.status_code, 201)
        self.assertEqual(1, len(children.get('added')))

        mail = children['added'].pop()
        self.assertEqual(mail.Title(), 'Hello')
        self.assertEqual(mail.message.filename, 'Hello.p7m')
        self.assertEqual(mail.original_message, None)

    @browsing
    def test_uses_title_if_given(self, browser):
        self.login(self.regular_user, browser)
        msg = base64.b64encode(load('mail_with_one_mail_attachment.eml'))

        with self.observe_children(self.dossier) as children:
            browser.open(
                self.dossier.absolute_url(),
                data=json.dumps({"@type": "ftw.mail.mail",
                                 "message": {"data": msg,
                                             "encoding": "base64",
                                             "filename": "testmail.eml"},
                                 "title": "Separate title"}),
                method='POST',
                headers=self.api_headers)

        self.assertEqual(browser.status_code, 201)
        self.assertEqual(1, len(children.get('added')))

        mail = children['added'].pop()
        self.assertEqual(mail.Title(), 'Separate title')
        self.assertEqual(mail.message.filename, 'Separate title.eml')
        self.assertEqual(mail.original_message, None)


class TestPatchMail(IntegrationTestCase):

    @browsing
    def test_updating_the_title(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.mail_eml.absolute_url(),
            data=json.dumps({'title': u'New title'}),
            method='PATCH',
            headers=self.api_headers)

        self.assertEqual(browser.status_code, 204)
        self.assertEqual(self.mail_eml.Title(), 'New title')
        self.assertEqual(self.mail_eml.title, u'New title')

    @browsing
    def test_updating_other_metadata(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.mail_eml.absolute_url(),
            data=json.dumps({'description': u'Lorem ipsum'}),
            method='PATCH',
            headers=self.api_headers)

        self.assertEqual(browser.status_code, 204)
        self.assertEqual(self.mail_eml.title, u'Die B\xfcrgschaft')
        self.assertEqual(self.mail_eml.description, 'Lorem ipsum')


class TestExtractAttachments(IntegrationTestCase):

    @browsing
    def test_extracts_all_when_no_positions_specified(self, browser):
        self.login(self.regular_user, browser)
        mail = create(Builder('mail')
                      .within(self.dossier)
                      .with_asset_message(
                          'mail_with_multiple_attachments.eml'))

        with self.observe_children(self.dossier) as children:
            browser.open(
                "/".join([mail.absolute_url(), "@extract-attachments"]),
                data=json.dumps({}),
                method='POST',
                headers=self.api_headers)

        self.assertEqual(browser.status_code, 200)
        self.assertEqual(3, len(mail.attachment_infos))
        self.assertEqual(3, len(children['added']))
        self.assertEqual(3, len(browser.json))

        expected_response = []
        for info in mail.attachment_infos:
            doc = uuidToObject(info['extracted_document_uid'])
            expected_response.append({
                'position': info['position'],
                'extracted_document_url': info['extracted_document_url'],
                'extracted_document_title': doc.title})

        self.assertItemsEqual(expected_response, browser.json)

    @browsing
    def test_extracts_attachment_specified_by_position(self, browser):
        self.login(self.regular_user, browser)
        mail = create(Builder('mail')
                      .within(self.dossier)
                      .with_asset_message(
                          'mail_with_multiple_attachments.eml'))

        with self.observe_children(self.dossier) as children:
            browser.open(
                "/".join([mail.absolute_url(), "@extract-attachments"]),
                data=json.dumps({'positions': [4]}),
                method='POST',
                headers=self.api_headers)

        self.assertEqual(browser.status_code, 200)
        self.assertEqual(1, len(children['added']))
        doc = children['added'].pop()
        info = mail._get_attachment_info(4)

        expected_response = [{
            'position': info['position'],
            'extracted_document_url': info['extracted_document_url'],
            'extracted_document_title': doc.title}]
        self.assertEqual(expected_response, browser.json)

    @browsing
    def test_returns_error_when_specified_positions_are_not_valid_for_extraction(self, browser):
        self.login(self.regular_user, browser)
        mail = create(Builder('mail')
                      .within(self.dossier)
                      .with_asset_message(
                          'mail_with_multiple_attachments.eml'))

        with self.observe_children(self.dossier) as children:
            with browser.expect_http_error(code=400, reason='Bad Request'):
                browser.open(
                    "/".join([mail.absolute_url(), "@extract-attachments"]),
                    data=json.dumps({'positions': [1]}),
                    method='POST',
                    headers=self.api_headers)

        self.assertEqual(0, len(children['added']))
        self.assertEqual({u'message': u'No attachment found at position 1.',
                          u'type': u'BadRequest'},
                         browser.json['error'])

    @browsing
    def test_returns_error_when_specified_attachment_is_already_extracted(self, browser):
        self.login(self.regular_user, browser)
        mail = create(Builder('mail')
                      .within(self.dossier)
                      .with_asset_message(
                          'mail_with_multiple_attachments.eml'))

        info = mail._get_attachment_info(4, write_modus=True)
        info['extracted'] = True
        with self.observe_children(self.dossier) as children:
            with browser.expect_http_error(code=400, reason='Bad Request'):
                browser.open(
                    "/".join([mail.absolute_url(), "@extract-attachments"]),
                    data=json.dumps({'positions': [4]}),
                    method='POST',
                    headers=self.api_headers)

        self.assertEqual(0, len(children['added']))
        self.assertEqual(
            {u'message': u'Attachment at position 4 has already been extracted to None.',
             u'type': u'BadRequest'},
            browser.json['error'])
