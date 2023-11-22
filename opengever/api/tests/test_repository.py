from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from plone import api
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import json


class TestRepositoryAPI(IntegrationTestCase):

    @browsing
    def test_can_get_repository_root(self, browser):
        language_tool = api.portal.get_tool('portal_languages')
        language_tool.addSupportedLanguage('fr-ch')

        self.login(self.regular_user, browser=browser)
        browser.open(self.repository_root, method="GET", headers={"Accept": "application/json"})
        self.assertEqual(200, browser.status_code)

        int_id = getUtility(IIntIds).getId(self.repository_root)
        expected_repository_root = {
            u'@components': {
                u'actions': {u'@id': u'http://nohost/plone/ordnungssystem/@actions'},
                u'breadcrumbs': {u'@id': u'http://nohost/plone/ordnungssystem/@breadcrumbs'},
                u'listing-stats': {u'@id': u'http://nohost/plone/ordnungssystem/@listing-stats'},
                u'lock': {u'@id': 'http://nohost/plone/ordnungssystem/@lock'},
                u"reference-number": {u"@id": u"http://nohost/plone/ordnungssystem/@reference-number"},
                u'main-dossier': None,
                u'navigation': {u'@id': u'http://nohost/plone/ordnungssystem/@navigation'},
                u'types': {u'@id': u'http://nohost/plone/ordnungssystem/@types'},
                u'workflow': {u'@id': u'http://nohost/plone/ordnungssystem/@workflow'},
            },
            u'@id': u'http://nohost/plone/ordnungssystem',
            u'@type': u'opengever.repository.repositoryroot',
            u'UID': u'createrepositorytree000000000001',
            u'allow_discussion': False,
            u'created': u'2016-08-31T07:01:33+00:00',
            u'id': u'ordnungssystem',
            u'is_folderish': True,
            u'items': [
                {
                    u'@id': u'http://nohost/plone/ordnungssystem/fuhrung',
                    u'@type': u'opengever.repository.repositoryfolder',
                    u'UID': u'createrepositorytree000000000002',
                    u'description': u'Alles zum Thema F\xfchrung.',
                    u'is_leafnode': False,
                    u'review_state': u'repositoryfolder-state-active',
                    u'title': u'1. F\xfchrung',
                },
                {
                    u'@id': u'http://nohost/plone/ordnungssystem/rechnungsprufungskommission',
                    u'@type': u'opengever.repository.repositoryfolder',
                    u'UID': u'createrepositorytree000000000004',
                    u'description': u'',
                    u'is_leafnode': True,
                    u'review_state': u'repositoryfolder-state-active',
                    u'title': u'2. Rechnungspr\xfcfungskommission',
                },
                {
                    u'@id': u'http://nohost/plone/ordnungssystem/spinnannetzregistrar',
                    u'@type': u'opengever.repository.repositoryfolder',
                    u'UID': u'createrepositorytree000000000005',
                    u'description': u'',
                    u'is_leafnode': True,
                    u'review_state': u'repositoryfolder-state-inactive',
                    u'title': u'3. Spinn\xe4nnetzregistrar',
                },
            ],
            u'items_total': 3,
            u'layout': u'tabbed_view',
            u'modified': u'2016-08-31T07:11:33+00:00',
            u"next_item": {
                u"@id": u"http://nohost/plone/vorlagen",
                u"@type": u"opengever.dossier.templatefolder",
                u"description": u"",
                u"title": u"Vorlagen"
            },
            u'oguid': 'plone:%s' % int_id,
            u'parent': {
                u'@id': u'http://nohost/plone',
                u'@type': u'Plone Site',
                u'description': u'',
                u'title': u'Plone site',
            },
            u"previous_item": {},
            u'reference_number_addendum': None,
            u'relative_path': u'ordnungssystem',
            u'review_state': u'repositoryroot-state-active',
            u'title_de': u'Ordnungssystem',
            u'title_fr': u'Syst\xe8me de classement',
            u'title_en': u'Ordnungssystem',
            u'valid_from': None,
            u'valid_until': None,
            u'version': None,

        }
        self.assert_json_structure_equal(expected_repository_root, browser.json)

    @browsing
    def test_admin_cannot_set_reference_number_addendum_field(self, browser):
        self.login(self.administrator, browser)

        browser.open(self.repository_root, method="PATCH", headers=self.api_headers,
                     data=json.dumps({'reference_number_addendum': 'NO'}))

        self.assertIsNone(self.repository_root.reference_number_addendum)

    @browsing
    def test_manager_can_set_reference_number_addendum_field(self, browser):
        self.login(self.manager, browser)

        browser.open(self.repository_root, method="PATCH", headers=self.api_headers,
                     data=json.dumps({'reference_number_addendum': 'NO'}))

        self.assertEqual(u'NO', self.repository_root.reference_number_addendum)

        browser.open(self.repository_root, method="GET", headers={"Accept": "application/json"})
        self.assertEqual(u'NO', browser.json['reference_number_addendum'])
