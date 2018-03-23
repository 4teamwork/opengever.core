from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.core.testing import OPENGEVER_FUNCTIONAL_PRIVATE_FOLDER_LAYER
from opengever.private.tests import create_members_folder
from opengever.testing import FunctionalTestCase
from plone import api
import transaction


class TestPrivateFolderWorkflow(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_PRIVATE_FOLDER_LAYER

    def setUp(self):
        super(TestPrivateFolderWorkflow, self).setUp()
        self.root = create(Builder('private_root'))

        private_policy_id = 'opengever_private_policy'
        # enable opengever.private placeful workflow policy
        self.root.manage_addProduct[
            'CMFPlacefulWorkflow'].manage_addWorkflowPolicyConfig()
        pwf_tool = api.portal.get_tool('portal_placeful_workflow')
        policy_config = pwf_tool.getWorkflowPolicyConfig(self.root)
        policy_config.setPolicyIn(private_policy_id, update_security=False)
        policy_config.setPolicyBelow(private_policy_id, update_security=False)

        self.folder = create_members_folder(self.root)
        self.hugo = create(Builder('user')
                           .named('Hugo', 'Boss')
                           .with_roles('Member', 'Reader'))
        self.admin = create(Builder('user')
                            .named('Ad', 'Min')
                            .with_roles('Member', 'Administrator'))
        self.member_admin = create(Builder('user')
                            .named('MemberAreaAdmin', 'MAdm')
                            .with_roles('Member',
                                        'MemberAreaAdministrator'))

    @browsing
    def test_only_owner_and_memberareaadmin_can_see_private_folder(self, browser):
        browser.login().open(self.folder)
        browser.login(self.member_admin).open(self.folder)
        with browser.expect_unauthorized():
            browser.login(self.hugo).open(self.folder)

        with browser.expect_unauthorized():
            browser.login(self.admin).open(self.folder)

    @browsing
    def test_owner_can_add_private_dossiers(self, browser):
        browser.login().open(self.folder)
        self.assertIn('Private Dossier', factoriesmenu.addable_types())

    @browsing
    def test_admin_cant_access_private_dossier(self, browser):
        dossier = create(Builder('private_dossier')
                         .within(self.folder)
                         .titled(u'Zuz\xfcge'))

        with browser.expect_unauthorized():
            browser.login(self.admin).open(dossier)

    @browsing
    def test_admin_cant_add_in_private_content(self, browser):
        dossier = create(Builder('private_dossier')
                         .within(self.folder)
                         .titled(u'Zuz\xfcge'))

        browser.login(self.member_admin)

        browser.open(self.folder)
        self.assertFalse(factoriesmenu.visible())

        browser.open(dossier)
        self.assertFalse(factoriesmenu.visible())

    @browsing
    def test_only_owner_and_memberareaadmin_can_see_private_dossiers(self, browser):
        dossier = create(Builder('private_dossier')
                         .within(self.folder)
                         .titled(u'Zuz\xfcge'))

        browser.login().visit(dossier)
        browser.login(self.member_admin).visit(dossier)
        with browser.expect_unauthorized():
            browser.login(self.hugo).visit(dossier)

    @browsing
    def test_only_owner_and_member_admins_can_see_private_documents(self, browser):
        dossier = create(Builder('private_dossier')
                         .within(self.folder)
                         .titled(u'Zuz\xfcge'))
        document = create(Builder('document')
                          .within(dossier)
                          .with_dummy_content()
                          .titled(u'Some File'))

        browser.login().visit(document)
        browser.login(self.member_admin).visit(document)

        with browser.expect_unauthorized():
            browser.login(self.admin).visit(document)
            browser.login(self.hugo).visit(document)

    @browsing
    def test_only_owner_and_member_admins_can_see_private_mails(self, browser):
        dossier = create(Builder('private_dossier')
                         .within(self.folder)
                         .titled(u'Zuz\xfcge'))
        mail = create(Builder('mail')
                      .within(dossier)
                      .with_dummy_message())

        browser.login().visit(mail)
        browser.login(self.member_admin).visit(mail)

        with browser.expect_unauthorized():
            browser.login(self.admin).visit(mail)
            browser.login(self.hugo).visit(mail)

    def test_make_sure_private_root_has_no_additional_local_roles(self):
        self.assertEquals({'test_user_1_': ['Owner']},
                          self.root.__ac_local_roles__)

    @browsing
    def test_moving_documents_out_of_private_area(self, browser):
        dossier = create(Builder('private_dossier')
                         .within(self.folder)
                         .titled(u'Zuz\xfcge'))
        document = create(Builder('document')
                          .within(dossier)
                          .with_dummy_content()
                          .titled(u'Some File'))

        public_dossier = create(Builder('dossier')
                                .titled(u'Public Dossier'))

        api.content.move(document, public_dossier)
        transaction.commit()

        # Other users should be allowed to view document in public repo
        pasted_document = public_dossier.objectValues()[0]
        browser.login(self.hugo).visit(pasted_document)

    @browsing
    def test_copying_documents_out_of_private_area(self, browser):
        dossier = create(Builder('private_dossier')
                         .within(self.folder)
                         .titled(u'Zuz\xfcge'))
        document = create(Builder('document')
                          .within(dossier)
                          .with_dummy_content()
                          .titled(u'Some File'))

        public_dossier = create(Builder('dossier')
                                .titled(u'Public Dossier'))

        api.content.copy(document, public_dossier)
        transaction.commit()

        # Other users should be allowed to view document in public repo
        pasted_document = public_dossier.objectValues()[0]
        browser.login(self.hugo).visit(pasted_document)
