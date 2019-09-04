from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.testbrowser import browsing
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import IntegrationTestCase
from plone import api
import json


class TestContentCreation(IntegrationTestCase):

    def setUp(self):
        super(TestContentCreation, self).setUp()
        self.portal = self.layer['portal']

        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de-ch')
        lang_tool.supported_langs = ['fr-ch', 'de-ch']

    @browsing
    def test_dossier_creation(self, browser):
        self.login(self.regular_user, browser)
        payload = {
            u'@type': u'opengever.dossier.businesscasedossier',
            u'title': u'Sanierung B\xe4rengraben 2016',
            u'responsible': self.regular_user.id,
            u'custody_period': 30,
            u'archival_value': u'unchecked',
            u'retention_period': 5,
        }
        response = browser.open(
            self.leaf_repofolder.absolute_url(),
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(201, response.status_code)

        new_object_id = str(response.json['id'])
        dossier = self.leaf_repofolder.restrictedTraverse(new_object_id)

        self.assertEqual(u'Sanierung B\xe4rengraben 2016', dossier.title)
        self.assertEqual(self.regular_user.id, IDossier(dossier).responsible)
        self.assertEqual(30, ILifeCycle(dossier).custody_period)
        self.assertEqual(u'unchecked', ILifeCycle(dossier).archival_value)
        self.assertEqual(5, ILifeCycle(dossier).retention_period)

    @browsing
    def test_document_creation(self, browser):
        self.login(self.regular_user, browser)
        payload = {
            u'@type': u'opengever.document.document',
            u'title': u'Sanierung B\xe4rengraben 2016',
            u'file': {
                u'data': u'TG9yZW0gSXBzdW0uCg==',
                u'encoding': u'base64',
                u'filename': u'b\xe4rengraben.txt',
                u'content-type': u'text/plain'},
        }
        response = browser.open(
            self.dossier.absolute_url(),
            data=json.dumps(payload),
            method='POST',
            headers=self.api_headers)

        self.assertEqual(201, response.status_code)

        new_object_id = str(response.json['id'])
        doc = self.dossier.restrictedTraverse(new_object_id)
        self.assertEqual(u'Sanierung B\xe4rengraben 2016', doc.title)
        self.assertEqual(u'Sanierung Baerengraben 2016.txt', doc.file.filename)

        checksum = IBumblebeeDocument(doc).get_checksum()
        self.assertIsNotNone(checksum)
