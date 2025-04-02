from ftw.testbrowser import browsing
from opengever.dossier.behaviors.protect_dossier import IProtectDossier
from opengever.testing import SolrIntegrationTestCase
import json


class TestProtectDossier(SolrIntegrationTestCase):

    @browsing
    def test_do_not_protect_dossier_by_default(self, browser):
        self.login(self.dossier_manager, browser=browser)

        data = {
            '@type': 'opengever.dossier.businesscasedossier',
            'title': 'Unprotected dossier',
            'responsible': self.dossier_manager.getId(),
        }

        with self.observe_children(self.leaf_repofolder) as children:
            browser.open(self.leaf_repofolder, data=json.dumps(data),
                         method='POST', headers=self.api_headers)

        self.assertEqual(201, browser.status_code)
        self.assertEqual(1, len(children['added']))
        dossier = children['added'].pop()

        self.assertFalse(IProtectDossier(dossier).is_dossier_protected())

        browser.open(dossier, data=json.dumps({'title': 'New title'}),
                     method='PATCH', headers=self.api_headers)

        self.assertEqual('New title', dossier.title)
        self.assertFalse(IProtectDossier(dossier).is_dossier_protected())

    @browsing
    def test_can_protect_dossier_on_post(self, browser):
        self.login(self.dossier_manager, browser=browser)

        data = {
            '@type': 'opengever.dossier.businesscasedossier',
            'title': 'Unprotected dossier',
            'responsible': self.dossier_manager.getId(),
            'reading': [self.regular_user.getId()],
            'dossier_manager': self.dossier_manager.getId()
        }

        with self.observe_children(self.leaf_repofolder) as children:
            browser.open(self.leaf_repofolder, data=json.dumps(data),
                         method='POST', headers=self.api_headers)

        self.assertEqual(201, browser.status_code)
        self.assertEqual(1, len(children['added']))
        dossier = children['added'].pop()

        self.assertTrue(IProtectDossier(dossier).is_dossier_protected())

    @browsing
    def test_can_protect_dossier_on_patch(self, browser):
        self.login(self.dossier_manager, browser=browser)
        self.assertFalse(IProtectDossier(self.dossier).is_dossier_protected())

        data = {
            'reading': [self.regular_user.getId()],
            'dossier_manager': self.dossier_manager.getId()
        }

        browser.open(self.dossier, data=json.dumps(data),
                     method='PATCH', headers=self.api_headers)

        self.assertTrue(IProtectDossier(self.dossier).is_dossier_protected())

    @browsing
    def test_only_dossier_manager_can_protect_dossier_on_post(self, browser):
        self.login(self.regular_user, browser=browser)

        data = {
            '@type': 'opengever.dossier.businesscasedossier',
            'title': 'Unprotected dossier',
            'responsible': self.dossier_manager.getId(),
            'reading': [self.regular_user.getId()],
            'dossier_manager': self.dossier_manager.getId()
        }

        browser.open(self.leaf_repofolder, data=json.dumps(data),
                     method='POST', headers=self.api_headers)

        self.assertFalse(IProtectDossier(self.dossier).is_dossier_protected())
        self.assertEqual([], self.dossier.reading)
        self.assertEqual([], self.dossier.reading_and_writing)
        self.assertEqual(None, self.dossier.dossier_manager)

    @browsing
    def test_only_dossier_manager_can_protect_dossier_on_patch(self, browser):
        self.login(self.regular_user, browser=browser)

        data = {
            'reading': [self.regular_user.getId()],
            'dossier_manager': self.dossier_manager.getId()
        }

        browser.open(self.dossier, data=json.dumps(data),
                     method='PATCH', headers=self.api_headers)

        self.assertFalse(IProtectDossier(self.dossier).is_dossier_protected())
        self.assertEqual([], self.dossier.reading)
        self.assertEqual([], self.dossier.reading_and_writing)
        self.assertEqual(None, self.dossier.dossier_manager)

    @browsing
    def test_can_remove_dossier_protection(self, browser):
        self.login(self.dossier_manager, browser=browser)

        data = {
            'reading': [self.regular_user.getId()],
            'dossier_manager': self.dossier_manager.getId()
        }

        browser.open(self.dossier, data=json.dumps(data),
                     method='PATCH', headers=self.api_headers)

        self.assertTrue(IProtectDossier(self.dossier).is_dossier_protected())

        browser.open(self.dossier, data=json.dumps({'reading': []}),
                     method='PATCH', headers=self.api_headers)

        self.assertFalse(IProtectDossier(self.dossier).is_dossier_protected())

    @browsing
    def test_can_change_role_inheritance(self, browser):
        self.login(self.dossier_manager, browser=browser)
        self.assertFalse(IProtectDossier(self.dossier).is_dossier_protected())

        data = {
            'reading': [self.regular_user.getId()],
            'dossier_manager': self.dossier_manager.getId(),
        }

        browser.open(self.dossier, data=json.dumps(data),
                     method='PATCH', headers=self.api_headers)

        self.assertTrue(IProtectDossier(self.dossier).is_dossier_protected())

        # Dossier protection blocks local roles by default
        self.assertTrue(self.dossier.__ac_local_roles_block__)

        # But can be changed by extending the local roles
        data = {
            'extend_local_roles': True,
        }

        browser.open(self.dossier, data=json.dumps(data),
                     method='PATCH', headers=self.api_headers)

        self.assertTrue(IProtectDossier(self.dossier).is_dossier_protected())
        self.assertFalse(self.dossier.__ac_local_roles_block__)
