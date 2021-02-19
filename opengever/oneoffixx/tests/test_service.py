from ftw.testbrowser import browsing
from opengever.oneoffixx.tests import BaseOneOffixxTestCase
from opengever.oneoffixx.utils import whitelisted_template_types
from zExceptions import BadRequest
from zope.annotation.interfaces import IAnnotations
import json


class TestCreateDocumentFromOneOffixxTemplate(BaseOneOffixxTestCase):

    def setUp(self):
        super(TestCreateDocumentFromOneOffixxTemplate, self).setUp()

        template_groups = [
            {
                'id': 'c2ddc01a-befd-4e0d-b15f-f67025f532be',
                'localizedName': 'Word templates',
                'templates': [self.template_word],
            },
        ]
        self.mock_oneoffixx_api_client(template_groups=template_groups)

    @browsing
    def test_raises_bad_request_if_no_template_id_is_provided(self, browser):
        self.login(self.dossier_responsible, browser)

        payload = {
            'document': {'title': 'My Oneoffixx document'},
        }

        browser.exception_bubbling = True
        with self.assertRaises(BadRequest) as cm:
            browser.open(
                self.dossier,
                method='POST',
                data=json.dumps(payload),
                headers=self.api_headers,
                view='@document_from_oneoffixx')

        self.assertEqual("Property 'template_id' is required.",
                         str(cm.exception))

    @browsing
    def test_raises_bad_request_if_template_id_does_not_exist(self, browser):
        self.login(self.dossier_responsible, browser)

        payload = {
            'document': {'title': 'My Oneoffixx document'},
            'template_id': 'not-existing-id'
        }

        browser.exception_bubbling = True
        with self.assertRaises(BadRequest) as cm:
            browser.open(
                self.dossier,
                method='POST',
                data=json.dumps(payload),
                headers=self.api_headers,
                view='@document_from_oneoffixx')

        self.assertEqual('The requested template_id does not exist.',
                         str(cm.exception))

    @browsing
    def test_creates_shadow_document_and_returns_oc_url(self, browser):
        self.login(self.dossier_responsible, browser)

        payload = {
            'document': {'title': 'My Oneoffixx document'},
            'template_id': self.template_word.get('id')
        }

        browser.open(
            self.dossier,
            method='POST',
            data=json.dumps(payload),
            headers=self.api_headers,
            view='@document_from_oneoffixx',
        )
        self.assertEqual(201, browser.status_code)
        self.assertIn('url', browser.json)
        self.assertTrue(browser.json['url'].startswith('oc:'))

        doc = self.dossier[browser.json['@id'].split('/')[-1]]
        self.assertTrue(doc.is_shadow_document())
        self.assertEqual('My Oneoffixx document', doc.Title())

        annotations = IAnnotations(doc)
        self.assertEqual(self.template_word['id'], annotations['template-id'])
        self.assertEqual(
            self.template_word['languages'], annotations['languages'])
        self.assertIn(
            self.template_word['localizedName'], annotations['filename'])
        self.assertEqual('3 Example Word file.docx', annotations['filename'])
        self.assertEqual(
            'application/vnd.openxmlformats-officedocument.wordprocessingml'
            '.document',
            annotations['content-type'],
        )

        whitelisted_content_types = [
            template['content-type']
            for template in whitelisted_template_types.values()
        ]
        self.assertIn(annotations['content-type'], whitelisted_content_types)

    @browsing
    def test_can_create_document_in_private_dossier(self, browser):
        self.login(self.regular_user, browser)

        payload = {
            'document': {'title': 'My Oneoffixx document'},
            'template_id': self.template_word.get('id')
        }

        browser.open(
            self.private_dossier,
            method='POST',
            data=json.dumps(payload),
            headers=self.api_headers,
            view='@document_from_oneoffixx',
        )
        self.assertEqual(201, browser.status_code)
        self.assertIn('url', browser.json)
        self.assertTrue(browser.json['url'].startswith('oc:'))

    @browsing
    def test_stores_additional_metadata(self, browser):
        self.login(self.dossier_responsible, browser)

        payload = {
            'document': {
                'title': 'My Oneoffixx document',
                'description': 'This is a description',
            },
            'template_id': self.template_word.get('id')
        }

        browser.open(
            self.dossier,
            method='POST',
            data=json.dumps(payload),
            headers=self.api_headers,
            view='@document_from_oneoffixx',
        )
        self.assertEqual(201, browser.status_code)
        doc = self.dossier[browser.json['@id'].split('/')[-1]]
        self.assertEqual('This is a description', doc.description)
