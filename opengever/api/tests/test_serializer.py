from ftw.bumblebee.interfaces import IBumblebeeDocument
from ftw.bumblebee.tests.helpers import DOCX_CHECKSUM
from ftw.testbrowser import browsing
from opengever.base.oguid import Oguid
from opengever.repository.behaviors.responsibleorg import IResponsibleOrgUnit
from opengever.testing import IntegrationTestCase
from plone import api
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxcontent import SerializeFolderToJson
from plone.restapi.serializer.dxcontent import SerializeToJson
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class TestSerializerSubclasses(IntegrationTestCase):
    """This needs to run as an IntegrationTestCase so that the ZCML is loaded
    which will trigger the imports of Python modules possibly containing our
    serializer subclasses. With a simple unittest, Python won't import them
    and therefore can't know about the subclasses.
    """

    whitelisted_subclasses = (
        'opengever.api.response.SerializeResponseToJson',
        'opengever.api.serializer.GeverSerializeFolderToJson',
        'opengever.api.serializer.GeverSerializeToJson',
    )

    def test_no_immediate_restapi_subclasses(self):
        for restapi_class in (SerializeFolderToJson, SerializeToJson):
            self.assert_no_immediate_subclasses(restapi_class)

    def assert_no_immediate_subclasses(self, restapi_class):
        subclasses = restapi_class.__subclasses__()
        for subclass in subclasses:
            name = '.'.join((subclass.__module__, subclass.__name__))
            if not name.startswith('opengever.'):
                continue

            if name not in self.whitelisted_subclasses:
                self.fail_with_msg(restapi_class, name)

    def fail_with_msg(self, upstream_class, offending_subclass):
        msg = (
            "%s is a direct subclass of plone.restapi's %s. This should be "
            "avoided, because that way GEVER specific serializer "
            "customizations that are supposed to apply to all content types "
            "won't be effective. Please subclass the appropriate "
            "serializer in opengever.api.serializer, or, if this is "
            "deliberate, whitelist the subclass in this test." % (
                offending_subclass, upstream_class.__name__))
        self.fail(msg)


class TestRepositoryFolderSerializer(IntegrationTestCase):

    def setUp(self):
        super(TestRepositoryFolderSerializer, self).setUp()
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de-ch')

    @browsing
    def test_repofolder_serialization_contains_reference_number(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.leaf_repofolder, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(u'Client1 1.1', browser.json.get(u'reference_number'))

    @browsing
    def test_repofolder_serialization_contains_blocked_local_roles(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.leaf_repofolder, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertIn('blocked_local_roles', browser.json)

    @browsing
    def test_repofolder_serialization_contains_is_leafnode(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.leaf_repofolder, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(True, browser.json.get(u'is_leafnode'))

    @browsing
    def test_repofolder_serialization_contains_relative_path(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.leaf_repofolder, headers=self.api_headers)
        self.assertEqual(browser.status_code, 200)
        self.assertEqual(
            u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen',
            browser.json.get(u'relative_path'))

    @browsing
    def test_repofolder_serialization_contains_oguid(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.leaf_repofolder, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        int_id = getUtility(IIntIds).getId(self.leaf_repofolder)
        self.assertEqual(
            u'plone:%s' % int_id,
            browser.json.get(u'oguid'))


class TestDossierSerializer(IntegrationTestCase):

    def setUp(self):
        super(TestDossierSerializer, self).setUp()
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de-ch')

    @browsing
    def test_dossier_serialization_contains_reference_number(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(u'Client1 1.1 / 1', browser.json.get(u'reference_number'))

    @browsing
    def test_dossier_serialization_contains_sequence_number(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(1, browser.json.get(u'sequence_number'))

    @browsing
    def test_dossier_serialization_contains_email(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(u'1014013300@example.org', browser.json.get(u'email'))

    @browsing
    def test_dossier_serialization_contains_responsible_fullname(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            u'Ziegler Robert', browser.json.get(u'responsible_fullname'))

    @browsing
    def test_dossier_serialization_contains_responsible_actor(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            {'@id': self.portal.absolute_url() + u'/@actors/robert.ziegler',
             'identifier': 'robert.ziegler'},
            browser.json.get(u'responsible_actor'))

    @browsing
    def test_dossier_serialization_contains_relative_path(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1',
            browser.json.get(u'relative_path'))

    @browsing
    def test_dossier_serialization_contains_is_subdossier(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            False,
            browser.json.get(u'is_subdossier'))

        browser.open(self.subdossier, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            True,
            browser.json.get(u'is_subdossier'))

    @browsing
    def test_dossier_serialization_contains_oguid(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        int_id = getUtility(IIntIds).getId(self.dossier)
        self.assertEqual(
            u'plone:%s' % int_id,
            browser.json.get(u'oguid'))


class TestDocumentSerializer(IntegrationTestCase):

    def setUp(self):
        super(TestDocumentSerializer, self).setUp()
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de-ch')

    @browsing
    def test_document_serialization_contains_reference_number(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(u'Client1 1.1 / 1 / 14', browser.json.get(u'reference_number'))

    @browsing
    def test_document_serialization_contains_sequence_number(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(14, browser.json.get(u'sequence_number'))

    @browsing
    def test_document_serialization_contains_bumblebee_checksum(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(DOCX_CHECKSUM, browser.json.get(u'bumblebee_checksum'))

    @browsing
    def test_document_serialization_contains_relative_path(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/{}'.format(
                self.document.getId()),
            browser.json.get(u'relative_path'))

    @browsing
    def test_document_serialization_contains_oguid(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        int_id = getUtility(IIntIds).getId(self.document)
        self.assertEqual(
            u'plone:%s' % int_id,
            browser.json.get(u'oguid'))

    @browsing
    def test_mail_serialization_contains_reference_number(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.mail_eml, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(u'Client1 1.1 / 1 / 29', browser.json.get(u'reference_number'))

    @browsing
    def test_mail_serialization_contains_bumblebee_checksum(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.mail_eml, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        checksum = IBumblebeeDocument(self.mail_eml).get_checksum()
        self.assertEqual(checksum, browser.json.get(u'bumblebee_checksum'))

    @browsing
    def test_mail_serialization_contains_relative_path(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.mail_eml, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(
            u'ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/{}'.format(
                self.mail_eml.getId()),
            browser.json.get(u'relative_path'))

    @browsing
    def test_mail_serialization_contains_oguid(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.mail_eml, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        int_id = getUtility(IIntIds).getId(self.mail_eml)
        self.assertEqual(
            u'plone:%s' % int_id,
            browser.json.get(u'oguid'))


class TestInboxSerializer(IntegrationTestCase):

    @browsing
    def test_inbox_serialization_contains_email(self, browser):
        self.login(self.secretariat_user, browser)
        browser.open(self.inbox, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(u'1011033300@example.org', browser.json.get(u'email'))

    @browsing
    def test_inbox_serialization_contains_inbox_id(self, browser):
        self.login(self.secretariat_user, browser)
        browser.open(self.inbox, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(u'inbox:fa', browser.json.get(u'inbox_id'))

    @browsing
    def test_inbox_id_defaults_to_current_orgunit(self, browser):
        self.login(self.manager, browser)
        IResponsibleOrgUnit(self.inbox).responsible_org_unit = None

        browser.open(self.inbox, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(u'inbox:fa', browser.json.get(u'inbox_id'))

        # change orgunit
        browser.open(self.repository_root)
        browser.css('.orgunitMenuContent a')[0].click()

        browser.open(self.inbox, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        self.assertEqual(u'inbox:rk', browser.json.get(u'inbox_id'))

    @browsing
    def test_inbox_serialization_contains_oguid(self, browser):
        self.login(self.secretariat_user, browser)
        browser.open(self.inbox, headers=self.api_headers)
        self.assertEqual(200, browser.status_code)
        int_id = getUtility(IIntIds).getId(self.inbox)
        self.assertEqual(u'plone:%s' % int_id, browser.json.get(u'oguid'))


class TestGroupSerializer(IntegrationTestCase):

    @browsing
    def test_group_serialization(self, browser):
        self.login(self.manager, browser)

        browser.open(
            self.portal, view='@groups/fa_users?b_size=1',
            headers=self.api_headers)
        self.assertEqual(200, browser.status_code)

        response = browser.json
        del response.get('users')['batching']
        self.assertEqual(
            {u'@id': u'http://nohost/plone/@groups/fa_users',
             u'@type': u'virtual.plone.group',
             u'description': u'',
             u'email': u'',
             u'groupname': u'fa_users',
             u'id': u'fa_users',
             u'roles': [u'Authenticated'],
             u'title': u'fa Users Group',
             u'users': {u'@id': u'http://nohost/plone/@groups/fa_users',
                        u'items': [{u'@id': u'http://nohost/plone/@users/service.user',
                                    u'@type': u'virtual.plone.user',
                                    u'title': u'User Service (service.user)',
                                    u'token': u'service.user'}],
                        u'items_total': 18}},
            response)


class TestOguidConverter(IntegrationTestCase):

    @browsing
    def test_oguid_converter(self, browser):
        self.login(self.manager, browser)

        oguid = Oguid.for_object(self.task)
        self.assertEqual(oguid.id, json_compatible(oguid))
