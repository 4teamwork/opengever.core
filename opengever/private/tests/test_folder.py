from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testing import freeze
from opengever.base.interfaces import IReferenceNumber
from opengever.core.testing import OPENGEVER_FUNCTIONAL_PRIVATE_FOLDER_LAYER
from opengever.private.tests import create_members_folder
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
from zExceptions import Unauthorized


class TestPrivateFolder(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_PRIVATE_FOLDER_LAYER

    def setUp(self):
        super(TestPrivateFolder, self).setUp()
        self.root = create(Builder('private_root'))
        self.folder = create_members_folder(self.root)

    @browsing
    def test_nesting_private_folders_is_disallowed(self, browser):
        browser.login().open(self.folder)
        self.assertEquals(['Private Dossier'], factoriesmenu.addable_types())

    def test_object_id_is_userid(self):
        self.assertEquals(TEST_USER_ID, self.folder.getId())

    def test_title_is_corresponding_users_label(self):
        self.assertEquals('Test User (test_user_1_)', self.folder.Title())

    def test_uses_userid_as_reference_number_part(self):
        self.assertEquals('Client1 test_user_1_',
                          IReferenceNumber(self.folder).get_number())

    def test_adds_additonal_roles_after_creation(self):
        self.assertEquals(
            ['Publisher', 'Authenticated', 'Owner', 'Editor', 'Reader',
             'Contributor', 'Reviewer'],
            api.user.get_roles(username=TEST_USER_ID, obj=self.folder))


class TestPrivateFolderTabbedView(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_PRIVATE_FOLDER_LAYER

    def setUp(self):
        super(TestPrivateFolderTabbedView, self).setUp()
        self.root = create(Builder('private_root'))
        self.folder = create_members_folder(self.root)

    @browsing
    def test_has_a_only_a_dossier_tab(self, browser):
        browser.login().open(self.folder)

        self.assertEquals(
            ['Dossiers'], browser.css('.formTab').text)

    @browsing
    def test_dossier_tab_lists_all_containig_private_dossiers(self, browser):
        with freeze(datetime(2015, 9, 1)):
            create(Builder('private_dossier')
                   .within(self.folder)
                   .titled(u'Zuz\xfcge'))
            create(Builder('private_dossier')
                   .within(self.folder)
                   .titled(u'Abg\xe4nge'))

        browser.login().open(self.folder,
                             view='tabbedview_view-dossiers')

        self.assertEquals(
            [['', 'Reference Number', 'Title', 'Review state',
              'Responsible', 'Start', 'End'],
             ['', 'Client1 test_user_1_ / 1', u'Zuz\xfcge',
              'dossier-state-active', '', '01.09.2015', ''],
             ['', 'Client1 test_user_1_ / 2', u'Abg\xe4nge',
              'dossier-state-active', '', '01.09.2015', '']],
            browser.css('.listing').first.lists())


    @browsing
    def test_copy_and_move_items_actions_are_disabled(self, browser):
        create(Builder('private_dossier')
               .within(self.folder)
               .titled(u'Zuz\xfcge'))

        browser.login().open(self.folder, view='tabbedview_view-dossiers')

        self.assertEquals(
            ['Export selection', 'Print selection (PDF)'],
            browser.css('.actionMenuContent a').text)


class TestPrivateFolderWorkflow(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_PRIVATE_FOLDER_LAYER

    def setUp(self):
        super(TestPrivateFolderWorkflow, self).setUp()
        self.root = create(Builder('private_root'))
        self.folder = create_members_folder(self.root)

    @browsing
    def test_only_owner_can_see_private_folder(self, browser):
        browser.login().open(self.folder)

        create(Builder('user')
               .named('Hugo', 'Boss')
               .with_roles('Editor', 'Contributor', 'Reader'))

        with self.assertRaises(Unauthorized):
            browser.login('hugo.boss').open(self.folder)

    @browsing
    def test_owner_can_add_private_dossiers(self, browser):
        browser.login().open(self.folder)
        self.assertIn('Private Dossier', factoriesmenu.addable_types())


class TestMyRepositoryAction(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_PRIVATE_FOLDER_LAYER

    def setUp(self):
        super(TestPrivateFolderWorkflow, self).setUp()
        self.root = create(Builder('private_root'))
        self.folder = create_members_folder(self.root)

    @browsing
    def is_show_when_private_folder_exists_and_redirects_to_homefolder(self, browser):
        browser.debug().login()

        self.assertIn('My Repository',
                      browser.css('#portal-globalnav li').text)

        browser.click_on('My Repository')
        self.assertEquals(self.folder.absolute_url(), browser.url)
