from base64 import b64encode
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.document.behaviors.customproperties import IDocumentCustomProperties
from opengever.propertysheets.utils import get_custom_properties
from opengever.testing import IntegrationTestCase
from opengever.testing.assets import path_to_asset
import json
import os


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


class TestDatetimeDeserialization(IntegrationTestCase):

    @browsing
    def test_date_field_deserializer_rejects_year_before_1900(self, browser):
        self.login(self.regular_user, browser)
        browser.raise_http_errors = False

        response = browser.open(
            self.document.absolute_url(),
            method='PATCH',
            headers=self.api_headers,
            data=json.dumps({'document_date': '1700-01-01'})
        )

        self.assertEqual(400, response.status_code)
        self.assertEqual('BadRequest', response.json['type'])
        self.assertIn("'field': 'document_date'", response.json['message'])
        self.assertIn("'year=1700 is invalid. Year must be >= 1900.'",
                      response.json['message'])

        response = browser.open(
            self.document,
            method='PATCH',
            headers=self.api_headers,
            data=json.dumps({'document_date': '1900-01-01'})
        )

        self.assertEqual(204, response.status_code)

    @browsing
    def test_utcdatetime_field_deserializer_rejects_year_before_1900(self, browser):
        self.login(self.workspace_member, browser)
        browser.raise_http_errors = False

        response = browser.open(
            self.workspace_meeting,
            method='PATCH',
            headers=self.api_headers,
            data=json.dumps({'start': '1700-01-01 13:45:00'})
        )

        self.assertEqual(400, response.status_code)
        self.assertEqual('BadRequest', response.json['type'])
        self.assertIn("'field': 'start'", response.json['message'])
        self.assertIn("'year=1700 is invalid. Year must be >= 1900.'",
                      response.json['message'])

        response = browser.open(
            self.workspace_meeting,
            method='PATCH',
            headers=self.api_headers,
            data=json.dumps({'start': '1900-01-01 13:45:00'})
        )

        self.assertEqual(204, response.status_code)


class TestCustomPropertiesDeserializer(IntegrationTestCase):

    @browsing
    def test_custom_properties_default_values_are_initialized(self, browser):
        self.login(self.manager)
        create(Builder("property_sheet_schema")
               .named("businesscase_dossier_schema")
               .assigned_to_slots(u"IDossier.dossier_type.businesscase")
               .with_field("textline", u"member", u"Member", u"", False, default_expression='member/getId'))

        self.login(self.regular_user, browser=browser)

        with self.observe_children(self.leaf_repofolder) as children:
            data = {"@type": "opengever.dossier.businesscasedossier",
                    "dossier_type": "businesscase",
                    "responsible": self.regular_user.id,
                    "title": "Testdossier A"}
            browser.open(
                self.leaf_repofolder.absolute_url(),
                method='POST',
                headers=self.api_headers,
                data=json.dumps(data)
            )

        self.assertEqual(1, len(children["added"]))
        dossier = children["added"].pop()

        self.assertEqual(
            self.regular_user.id,
            get_custom_properties(dossier)['member'])

    @browsing
    def test_custom_properties_default_values_are_initialized_for_active_and_default_slots(self, browser):
        self.login(self.manager)
        create(
            Builder("property_sheet_schema")
            .named("schema3")
            .assigned_to_slots(u"IDocumentMetadata.document_type.question")
            .with_field("text", u"foo1", u"title 1", u"", False)
            .with_field("text", u"foo2", u"title 2", u"", False, default=u"bla")
        )

        create(
            Builder("property_sheet_schema")
            .named("schem4")
            .assigned_to_slots(u"IDocument.default")
            .with_field("text", u"bar1", u"title 1", u"", False)
            .with_field("text", u"bar2", u"title 2", u"", False, default=u"bli")
        )

        create(
            Builder("property_sheet_schema")
            .named("schema5")
            .assigned_to_slots(u"IDocumentMetadata.document_type.offer")
            .with_field("text", u"baz1", u"title 1", u"", False)
            .with_field("text", u"baz2", u"title 2", u"", False, default=u"blu")
        )

        self.login(self.regular_user, browser=browser)

        with self.observe_children(self.empty_dossier) as children:
            data = {"@type": "opengever.document.document",
                    "document_type": "question",
                    "file": {
                        "data": "foo bar",
                        "filename": "test.txt"},
                    }
            browser.open(
                self.empty_dossier.absolute_url(),
                method='POST',
                headers=self.api_headers,
                data=json.dumps(data)
            )

        self.assertEqual(1, len(children["added"]))
        document = children["added"].pop()

        self.assertEqual(
            {'bar1': None, 'bar2': u'bli', 'foo1': None, 'foo2': u'bla'},
            get_custom_properties(document))
        self.assertEqual(
            {'IDocumentMetadata.document_type.question': {'foo2': u'bla'},
             'IDocument.default': {'bar2': u'bli'}},
            IDocumentCustomProperties(document).custom_properties)

    @browsing
    def test_custom_properties_default_values_are_not_initialized_for_inactive_slots(self, browser):
        self.login(self.manager)

        create(
            Builder("property_sheet_schema")
            .named("schema3")
            .assigned_to_slots(u"IDocumentMetadata.document_type.offer")
            .with_field("text", u"baz1", u"title 1", u"", False)
            .with_field("text", u"baz2", u"title 2", u"", False, default=u"blu")
        )

        self.login(self.regular_user, browser=browser)

        with self.observe_children(self.empty_dossier) as children:
            data = {"@type": "opengever.document.document",
                    "document_type": "question",
                    "file": {
                        "data": "foo bar",
                        "filename": "test.txt"},
                    }
            browser.open(
                self.empty_dossier.absolute_url(),
                method='POST',
                headers=self.api_headers,
                data=json.dumps(data)
            )

        self.assertEqual(1, len(children["added"]))
        document = children["added"].pop()

        self.assertEqual({}, get_custom_properties(document))
        self.assertEqual(None, IDocumentCustomProperties(document).custom_properties)

    @browsing
    def test_update_custom_property_value_when_the_previous_value_contained_an_umlaut(self, browser):
        self.login(self.manager)
        choices = ['one', u'zw\xf6i']
        create(
            Builder('property_sheet_schema')
            .named('schema')
            .assigned_to_slots(u'IDossier.dossier_type.businesscase')
            .with_field('choice', u'choose', u'Choose', u'', False, values=choices, default=u'zw\xf6i')
        )

        self.login(self.regular_user, browser=browser)

        dossier = create(Builder('dossier')
                         .within(self.leaf_repofolder)
                         .having(
                             dossier_type='businesscase',
                             custom_properties={
                                 'IDossier.dossier_type.businesscase':
                                     {'choose': u"zw\xf6i"}}))

        data = browser.open(dossier, headers=self.api_headers).json
        custom_field = data.get('custom_properties').get(
            'IDossier.dossier_type.businesscase').get('choose')

        self.assertEqual(u'zw\xf6i', custom_field.get('title'))

        browser.open(dossier, method='PATCH',
                     data=json.dumps({
                         'custom_properties': {
                             'IDossier.dossier_type.businesscase': {
                                 'choose': 'one'
                             }
                         }
                     }), headers=self.api_headers)

        data = browser.open(dossier, headers=self.api_headers).json
        custom_field = data.get('custom_properties').get(
            'IDossier.dossier_type.businesscase').get('choose')

        self.assertEqual(u'one', custom_field.get('title'))
