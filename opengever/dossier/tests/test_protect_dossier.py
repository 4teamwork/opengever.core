from ftw.testbrowser import browsing
from opengever.dossier.behaviors.protect_dossier import IProtectDossier
from opengever.testing import IntegrationTestCase
from plone import api


class TestProtectDossier(IntegrationTestCase):

    def test_user_has_no_permission_if_not_dossier_manager(self):
        """ This test is related to the other test. We have to validate
        that the regular user is not allowed to protect dossiers by default.

        The problem is, that the permission-check will be cached very strong and it is
        painful to reset the cache (i.e. creating a new request, change user roles or
        change the path of the object.).
        """
        self.login(self.regular_user)

        self.assertFalse(
            api.user.has_permission('opengever.dossier: Protect dossier',
                                    obj=self.dossier))

    def test_user_has_dossier_protect_permission_if_it_has_dossier_manager_on_repo_root(self):
        self.login(self.regular_user)

        self.repository_root.manage_setLocalRoles(self.regular_user.getId(), ('DossierManager', ))

        self.assertTrue(
            api.user.has_permission('opengever.dossier: Protect dossier',
                                    obj=self.dossier))

    def test_user_has_permission_if_dossier_manager_on_repo(self):
        self.login(self.regular_user)

        self.leaf_repofolder.manage_setLocalRoles(self.regular_user.getId(), ('DossierManager', ))

        self.assertTrue(
            api.user.has_permission('opengever.dossier: Protect dossier',
                                    obj=self.dossier))

    def test_user_has_no_permission_to_protect_dossier_if_repo_folder_is_inactive(self):
        self.login(self.dossier_manager)

        self.assertTrue(
            api.user.has_permission('opengever.dossier: Protect dossier',
                                    obj=self.dossier))

        self.set_workflow_state(
            'repositoryfolder-state-inactive', self.leaf_repofolder)

        self.assertFalse(
            api.user.has_permission('opengever.dossier: Protect dossier',
                                    obj=self.dossier))


class TestProtectDossierBehavior(IntegrationTestCase):

    @browsing
    def test_regular_user_cannot_see_protect_dossier_fields(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.dossier, view="@@edit")

        self.assertEqual(
            0, len(browser.css('select#form-widgets-IProtectDossier-reading')))

        self.assertEqual(
            0, len(browser.css('select#form-widgets-IProtectDossier-reading_and_writing')))

    @browsing
    def test_dossier_manager_can_see_protect_dossier_fields(self, browser):
        self.login(self.dossier_manager, browser)

        browser.open(self.dossier, view="@@edit")

        self.assertEqual(
            1, len(browser.css('select#form-widgets-IProtectDossier-reading')))

        self.assertEqual(
            1, len(browser.css('select#form-widgets-IProtectDossier-reading_and_writing')))

    @browsing
    def test_dossier_manager_can_set_protect_dossier_fields(self, browser):
        self.login(self.dossier_manager, browser)

        browser.open(self.dossier, view="@@edit")

        form = browser.find_form_by_field('Reading')
        form.find_widget('Reading').fill('projekt_a')
        form.find_widget('Reading and writing').fill('projekt_b')
        browser.click_on('Save')

        self.assertEqual(['projekt_a'], IProtectDossier(self.dossier).reading)
        self.assertEqual(['projekt_b'], IProtectDossier(self.dossier).reading_and_writing)
