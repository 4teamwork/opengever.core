from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.testing import IntegrationTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
from zExceptions import Unauthorized


class TestPrivateFolderWorkflow(IntegrationTestCase):

    features = ('private', )

    @browsing
    def test_only_owner_and_memberareaadmin_can_see_private_folder(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.private_folder)

        self.login(self.member_admin, browser=browser)
        browser.open(self.private_folder)

        with self.assertRaises(Unauthorized):
            self.login(self.dossier_responsible, browser=browser)
            browser.open(self.private_folder)

        with self.assertRaises(Unauthorized):
            self.login(self.administrator, browser=browser)
            browser.open(self.private_folder)

        with self.assertRaises(Unauthorized):
            self.login(self.limited_admin, browser=browser)
            browser.open(self.private_folder)

    @browsing
    def test_owner_can_add_private_dossiers(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.private_folder)
        self.assertIn('Private Dossier', factoriesmenu.addable_types())

    @browsing
    def test_admin_cant_access_private_dossier(self, browser):
        self.login(self.administrator, browser=browser)

        with self.assertRaises(Unauthorized):
            browser.open(self.private_dossier)

    @browsing
    def test_limited_admin_cant_access_private_dossier(self, browser):
        self.login(self.limited_admin, browser=browser)

        with self.assertRaises(Unauthorized):
            browser.open(self.private_dossier)

    @browsing
    def test_member_admin_cant_add_in_private_content(self, browser):
        self.login(self.member_admin, browser=browser)

        browser.open(self.private_folder)
        self.assertFalse(factoriesmenu.visible())

        browser.open(self.private_dossier)
        self.assertFalse(factoriesmenu.visible())

    @browsing
    def test_only_owner_and_memberareaadmin_can_see_private_dossiers(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.private_dossier)

        self.login(self.member_admin, browser=browser)
        browser.open(self.private_dossier)

        with self.assertRaises(Unauthorized):
            self.login(self.dossier_responsible, browser=browser)
            browser.open(self.private_dossier)

        with self.assertRaises(Unauthorized):
            self.login(self.administrator, browser=browser)
            browser.open(self.private_dossier)

    @browsing
    def test_only_owner_and_member_admins_can_see_private_documents(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.private_document)

        self.login(self.member_admin, browser=browser)
        browser.open(self.private_document)

        with self.assertRaises(Unauthorized):
            self.login(self.dossier_responsible, browser=browser)
            browser.open(self.private_document)

        with self.assertRaises(Unauthorized):
            self.login(self.administrator, browser=browser)
            browser.open(self.private_document)

    @browsing
    def test_only_owner_and_member_admins_can_see_private_mails(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.private_mail)

        self.login(self.member_admin, browser=browser)
        browser.open(self.private_mail)

        with self.assertRaises(Unauthorized):
            self.login(self.dossier_responsible, browser=browser)
            browser.open(self.private_mail)

        with self.assertRaises(Unauthorized):
            self.login(self.administrator, browser=browser)
            browser.open(self.private_mail)

    def test_make_sure_private_root_has_no_additional_local_roles(self):
        self.login(self.regular_user)

        self.assertEquals({TEST_USER_ID: ['Owner']},
                          self.private_root.__ac_local_roles__)

    @browsing
    def test_moving_documents_out_of_private_area(self, browser):
        self.login(self.regular_user)
        document = api.content.move(self.private_document, self.dossier)

        # Other users should be allowed to view document in public repo
        self.login(self.regular_user, browser=browser)
        browser.open(document)

    @browsing
    def test_copying_documents_out_of_private_area(self, browser):
        self.login(self.regular_user)
        copy = api.content.copy(self.private_document, self.dossier)

        # Other users should be allowed to view document in public repo
        self.login(self.regular_user, browser=browser)
        browser.open(copy)
