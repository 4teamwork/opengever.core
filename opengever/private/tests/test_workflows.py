from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.core.testing import OPENGEVER_FUNCTIONAL_PRIVATE_FOLDER_LAYER
from opengever.private.tests import create_members_folder
from opengever.testing import FunctionalTestCase


class TestPrivateFolderWorkflow(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_PRIVATE_FOLDER_LAYER

    def setUp(self):
        super(TestPrivateFolderWorkflow, self).setUp()
        self.root = create(Builder('private_root'))
        self.folder = create_members_folder(self.root)

        self.hugo = create(Builder('user')
                           .named('Hugo', 'Boss')
                           .with_roles('Member'))
        self.admin = create(Builder('user')
                            .named('Ad', 'Min')
                            .with_roles('Member', 'Administrator'))

    @browsing
    def test_only_owner_and_admin_can_see_private_folder(self, browser):
        browser.login().open(self.folder)
        browser.login(self.admin).open(self.folder)
        with browser.expect_unauthorized():
            browser.login(self.hugo).open(self.folder)

    @browsing
    def test_owner_can_add_private_dossiers(self, browser):
        browser.login().open(self.folder)
        self.assertIn('Private Dossier', factoriesmenu.addable_types())

    @browsing
    def test_admin_cant_add_in_private_content(self, browser):
        dossier = create(Builder('private_dossier')
                         .within(self.folder)
                         .titled(u'Zuz\xfcge'))

        browser.login(self.admin)

        browser.open(self.folder)
        self.assertFalse(factoriesmenu.visible())

        browser.open(dossier)
        self.assertFalse(factoriesmenu.visible())

    @browsing
    def test_only_owner_and_admin_can_see_private_dossiers(self, browser):
        dossier = create(Builder('private_dossier')
                         .within(self.folder)
                         .titled(u'Zuz\xfcge'))

        browser.login().visit(dossier)
        browser.login(self.admin).visit(dossier)
        with browser.expect_unauthorized():
            browser.login(self.hugo).visit(dossier)

    @browsing
    def test_only_owner_and_admin_can_see_private_documents(self, browser):
        dossier = create(Builder('private_dossier')
                         .within(self.folder)
                         .titled(u'Zuz\xfcge'))
        document = create(Builder('document')
                          .within(dossier)
                          .with_dummy_content()
                          .titled(u'Some File'))

        browser.login().visit(document)
        browser.login(self.admin).visit(document)
        with browser.expect_unauthorized():
            browser.login(self.hugo).visit(document)

    def test_make_sure_private_root_has_no_additional_local_roles(self):
        self.assertEquals({'test_user_1_': ['Owner']},
                          self.root.__ac_local_roles__)
