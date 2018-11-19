from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.bumblebee.tests.helpers import DOCX_CHECKSUM
from ftw.testbrowser import restapi
from opengever.testing import IntegrationTestCase
from plone import api


class TestApiSerializer(IntegrationTestCase):

    def setUp(self):
        super(TestApiSerializer, self).setUp()
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de-ch')


class TestRepositoryFolderSerializer(TestApiSerializer):

    @restapi
    def test_repofolder_serialization_contains_reference_number(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.leaf_repofolder)
        self.assertEqual(200, api_client.status_code)
        self.assertEqual(u'Client1 1.1', api_client.contents.get(u'reference_number'))

    @restapi
    def test_repofolder_serialization_contains_is_leafnode(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.leaf_repofolder)
        self.assertEqual(200, api_client.status_code)
        self.assertEqual(True, api_client.contents.get(u'is_leafnode'))

    @restapi
    def test_repofolder_serialization_contains_relative_path(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.leaf_repofolder)
        self.assertEqual(200, api_client.status_code)
        self.assertEqual(u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen', api_client.contents.get(u'relative_path'))


class TestDossierSerializer(TestApiSerializer):

    @restapi
    def test_dossier_serialization_contains_reference_number(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.dossier)
        self.assertEqual(200, api_client.status_code)
        self.assertEqual(u'Client1 1.1 / 1', api_client.contents.get(u'reference_number'))

    @restapi
    def test_dossier_serialization_contains_email(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.dossier)
        self.assertEqual(200, api_client.status_code)
        self.assertEqual(u'1014013300@example.org', api_client.contents.get(u'email'))

    @restapi
    def test_dossier_serialization_contains_responsible_fullname(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.dossier)
        self.assertEqual(200, api_client.status_code)
        self.assertEqual(u'Ziegler Robert', api_client.contents.get(u'responsible_fullname'))

    @restapi
    def test_dossier_serialization_contains_relative_path(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.dossier)
        self.assertEqual(200, api_client.status_code)
        self.assertEqual(
            u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1',
            api_client.contents.get(u'relative_path'),
        )


class TestDocumentSerializer(TestApiSerializer):

    @restapi
    def test_document_serialization_contains_reference_number(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.document)
        self.assertEqual(200, api_client.status_code)
        self.assertEqual(u'Client1 1.1 / 1 / 12', api_client.contents.get(u'reference_number'))

    @restapi
    def test_document_serialization_contains_bumblebee_checksum(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.document)
        self.assertEqual(200, api_client.status_code)
        self.assertEqual(DOCX_CHECKSUM, api_client.contents.get(u'bumblebee_checksum'))

    @restapi
    def test_document_serialization_contains_relative_path(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.document)
        self.assertEqual(200, api_client.status_code)
        self.assertEqual(
            u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/{}'.format(self.document.getId()),
            api_client.contents.get(u'relative_path'),
        )

    @restapi
    def test_mail_serialization_contains_reference_number(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.mail_eml)
        self.assertEqual(200, api_client.status_code)
        self.assertEqual(u'Client1 1.1 / 1 / 24', api_client.contents.get(u'reference_number'))

    @restapi
    def test_mail_serialization_contains_bumblebee_checksum(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.mail_eml)
        self.assertEqual(200, api_client.status_code)

        checksum = IBumblebeeDocument(self.mail_eml).get_checksum()
        self.assertEqual(checksum, api_client.contents.get(u'bumblebee_checksum'))

    @restapi
    def test_mail_serialization_contains_relative_path(self, api_client):
        self.login(self.regular_user, api_client)
        api_client.open(self.mail_eml)
        self.assertEqual(200, api_client.status_code)
        self.assertEqual(
            u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/{}'.format(self.mail_eml.getId()),
            api_client.contents.get(u'relative_path'),
        )
