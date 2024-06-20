from ftw.testbrowser import browsing
from opengever.oneoffixx.tests import BaseOneOffixxTestCase
from opengever.oneoffixx.utils import whitelisted_template_types
from zExceptions import BadRequest
from zope.annotation.interfaces import IAnnotations
import json


class TestCreateDocumentFromOneOffixxTemplate(BaseOneOffixxTestCase):

    @browsing
    def test_creates_shadow_document_and_returns_oc_url(self, browser):
        self.login(self.dossier_responsible, browser)

        payload = {
            'document': {'title': 'My Oneoffixx document'},
            'filetype': {'token': 'GeverWord', 'title': 'Word'}
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
        self.assertEqual('My Oneoffixx document', doc.title)
        self.assertEqual(u'oneoffixx_from_template.docx', annotations['filename'])
        self.assertEqual(u'GeverWord', annotations['tag'])

    @browsing
    def test_can_create_document_in_private_dossier(self, browser):
        self.login(self.regular_user, browser)

        payload = {
            'document': {'title': 'My Oneoffixx document'},
            'filetype': {'token': 'GeverWord', 'title': 'Word'}
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
            'filetype': {'token': 'GeverWord', 'title': 'Word'}
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
