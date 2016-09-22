from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testing import freeze
from opengever.base.interfaces import IReferenceNumber
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
from zExceptions import Unauthorized


class TestPrivateFolder(FunctionalTestCase):

    @browsing
    def test_is_addable_on_private_root(self, browser):
        self.grant('Manager')

        root = create(Builder('private_root'))

        browser.login().open(root)
        factoriesmenu.add('Private folder')
        browser.fill({'User ID': u'franz.mueller'})
        browser.click_on('Save')

        self.assertEquals([u'franz.mueller'], browser.css('h1').text)

    @browsing
    def test_is_only_addable_by_manager(self, browser):
        root = create(Builder('private_root'))

        with self.assertRaises(Unauthorized):
            browser.login().open(root, view='++add++opengever.private.folder')
            browser.fill({'User ID': TEST_USER_ID})
            browser.click_on('Save')

    @browsing
    def test_nesting_private_folders_is_disallowed(self, browser):
        root = create(Builder('private_root'))
        folder = create(Builder('private_folder')
                        .within(root)
                        .having(userid=TEST_USER_ID))

        browser.login().open(folder)
        self.assertEquals(['Private Dossier'], factoriesmenu.addable_types())

    def test_object_id_is_userid(self):
        folder = create(Builder('private_folder').having(userid=TEST_USER_ID))
        self.assertEquals(TEST_USER_ID, folder.getId())

    def test_title_is_corresponding_users_label(self):
        folder = create(Builder('private_folder').having(userid=TEST_USER_ID))
        self.assertEquals('Test User (test_user_1_)', folder.Title())

    def test_uses_userid_as_reference_number_part(self):
        folder = create(Builder('private_folder').having(userid=TEST_USER_ID))

        self.assertEquals('Client1 test_user_1_',
                          IReferenceNumber(folder).get_number())


class TestPrivateFolderTabbedView(FunctionalTestCase):

    def setUp(self):
        super(TestPrivateFolderTabbedView, self).setUp()
        self.root = create(Builder('private_root'))
        self.folder = create(Builder('private_folder')
                             .having(userid=TEST_USER_ID))

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


class TestPrivateFolderWorkflow(FunctionalTestCase):

    def setUp(self):
        super(TestPrivateFolderWorkflow, self).setUp()
        self.root = create(Builder('private_root'))
        self.folder = create(Builder('private_folder')
                             .within(self.root)
                             .having(userid=TEST_USER_ID))

        create(Builder('user')
               .named('Hugo', 'Boss')
               .with_roles('Administrator', 'Editor', 'Contributor', 'Reader'))

    @browsing
    def test_only_owner_can_see_private_folder(self, browser):
        browser.login().open(self.folder)

        with self.assertRaises(Unauthorized):
            browser.login('hugo.boss').open(self.folder)

    @browsing
    def test_owner_can_add_private_dossiers(self, browser):
        browser.login().open(self.folder)
        self.assertIn('Private Dossier', factoriesmenu.addable_types())
