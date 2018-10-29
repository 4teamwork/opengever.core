from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.testbrowser import restapi
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import IntegrationTestCase
from plone import api


class TestContentCreation(IntegrationTestCase):

    def setUp(self):
        super(TestContentCreation, self).setUp()
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de-ch')
        lang_tool.supported_langs = ['fr-ch', 'de-ch']

    @restapi
    def test_dossier_creation(self, api_client):
        self.login(self.regular_user, api_client)
        payload = {
            u'@type': u'opengever.dossier.businesscasedossier',
            u'title': u'Sanierung B\xe4rengraben 2016',
            u'responsible': self.regular_user.id,
            u'custody_period': 30,
            u'archival_value': u'unchecked',
            u'retention_period': 5,
        }
        api_client.open(self.leaf_repofolder, data=payload)
        self.assertEqual(201, api_client.status_code)

        new_object_id = str(api_client.contents['id'])
        dossier = self.leaf_repofolder.restrictedTraverse(new_object_id)

        self.assertEqual(u'Sanierung B\xe4rengraben 2016', dossier.title)
        self.assertEqual(self.regular_user.id, IDossier(dossier).responsible)
        self.assertEqual(30, ILifeCycle(dossier).custody_period)
        self.assertEqual(u'unchecked', ILifeCycle(dossier).archival_value)
        self.assertEqual(5, ILifeCycle(dossier).retention_period)

    @restapi
    def test_document_creation(self, api_client):
        self.login(self.regular_user, api_client)
        payload = {
            u'@type': u'opengever.document.document',
            u'title': u'Sanierung B\xe4rengraben 2016',
            u'file': {
                u'data': u'TG9yZW0gSXBzdW0uCg==',
                u'encoding': u'base64',
                u'filename': u'b\xe4rengraben.txt',
                u'content-type': u'text/plain'},
        }
        api_client.open(self.dossier, data=payload)
        self.assertEqual(201, api_client.status_code)

        new_object_id = str(api_client.contents['id'])
        doc = self.dossier.restrictedTraverse(new_object_id)
        self.assertEqual(u'Sanierung B\xe4rengraben 2016', doc.title)
        self.assertEqual(u'Sanierung Baerengraben 2016.txt', doc.file.filename)

        checksum = IBumblebeeDocument(doc).get_checksum()
        self.assertIsNotNone(checksum)
