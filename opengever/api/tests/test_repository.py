from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestRepositoryAPI(IntegrationTestCase):
    @browsing
    def test_can_get_repository_root(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.repository_root, method="GET", headers={"Accept": "application/json"})
        self.assertEqual(200, browser.status_code)
        expected_repository_root = {
            u'@components': {
                u'actions': {u'@id': u'http://nohost/plone/ordnungssystem/@actions'},
                u'breadcrumbs': {u'@id': u'http://nohost/plone/ordnungssystem/@breadcrumbs'},
                u'navigation': {u'@id': u'http://nohost/plone/ordnungssystem/@navigation'},
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
                    u'description': u'Alles zum Thema F\xfchrung.',
                    u'review_state': u'repositoryfolder-state-active',
                    u'title': None,
                },
                {
                    u'@id': u'http://nohost/plone/ordnungssystem/rechnungsprufungskommission',
                    u'@type': u'opengever.repository.repositoryfolder',
                    u'description': u'',
                    u'review_state': u'repositoryfolder-state-active',
                    u'title': None,
                },
                {
                    u'@id': u'http://nohost/plone/ordnungssystem/spinnannetzregistrar',
                    u'@type': u'opengever.repository.repositoryfolder',
                    u'description': u'',
                    u'review_state': u'repositoryfolder-state-inactive',
                    u'title': None,
                },
            ],
            u'items_total': 3,
            u'layout': u'tabbed_view',
            u'modified': u'2016-08-31T07:09:33+00:00',
            u'parent': {
                u'@id': u'http://nohost/plone',
                u'@type': u'Plone Site',
                u'description': u'',
                u'title': u'Plone site',
            },
            u'relative_path': u'ordnungssystem',
            u'review_state': u'repositoryroot-state-active',
            u'title_de': u'Ordnungssystem',
            u'title_fr': u'Syst\xe8me de classement',
            u'valid_from': None,
            u'valid_until': None,
            u'version': None,
        }
        self.assertEqual(expected_repository_root, browser.json)
