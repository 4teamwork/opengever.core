from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestRepositoryAPI(IntegrationTestCase):
    @browsing
    def test_can_get_repository_root(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.repository_root, method="GET", headers={"Accept": "application/json"})
        self.assertEqual(200, browser.status_code)
        expected_repository_root = {
            u"title_de": u"Ordnungssystem",
            u"valid_until": None,
            u"title_fr": u"Syst\xe8me de classement",
            u"layout": u"tabbed_view",
            u"UID": u"createrepositorytree000000000001",
            u"parent": {
                u"title": u"Plone site",
                u"@id": u"http://nohost/plone",
                u"@type": u"Plone Site",
                u"description": u"",
            },
            u"created": u"2016-08-31T06:01:33+00:00",
            u"is_folderish": True,
            u"modified": u"2016-08-31T06:07:33+00:00",
            u"allow_discussion": False,
            u"id": u"ordnungssystem",
            u"items_total": 2,
            u"valid_from": None,
            u"version": None,
            u"@components": {
                u"breadcrumbs": {u"@id": u"http://nohost/plone/ordnungssystem/@breadcrumbs"},
                u"navigation": {u"@id": u"http://nohost/plone/ordnungssystem/@navigation"},
                u"actions": {u"@id": u"http://nohost/plone/ordnungssystem/@actions"},
                u"workflow": {u"@id": u"http://nohost/plone/ordnungssystem/@workflow"},
            },
            u"review_state": u"repositoryroot-state-active",
            u"items": [
                {
                    u"review_state": u"repositoryfolder-state-active",
                    u"title": None,
                    u"@id": u"http://nohost/plone/ordnungssystem/fuhrung",
                    u"@type": u"opengever.repository.repositoryfolder",
                    u"description": u"Alles zum Thema F\xfchrung.",
                },
                {
                    u"review_state": u"repositoryfolder-state-active",
                    u"title": None,
                    u"@id": u"http://nohost/plone/ordnungssystem/rechnungsprufungskommission",
                    u"@type": u"opengever.repository.repositoryfolder",
                    u"description": u"",
                },
            ],
            u"@id": u"http://nohost/plone/ordnungssystem",
            u"@type": u"opengever.repository.repositoryroot",
        }
        self.assertEqual(expected_repository_root, browser.json)
