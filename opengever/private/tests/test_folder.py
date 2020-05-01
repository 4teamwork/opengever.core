from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.base.interfaces import IReferenceNumber
from opengever.private.tests import create_members_folder
from opengever.testing import IntegrationTestCase
from opengever.testing import SolrIntegrationTestCase
from plone import api


class TestPrivateFolder(IntegrationTestCase):

    features = ('private',)

    @browsing
    def test_nesting_private_folders_is_disallowed(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.private_folder)
        self.assertEquals(['Private Dossier'], factoriesmenu.addable_types())

    def test_object_id_is_userid(self):
        self.login(self.regular_user)
        self.assertEquals('kathi-barfuss', self.private_folder.getId())

    def test_Title_is_corresponding_users_label(self):
        self.login(self.regular_user)
        self.assertEquals('B\xc3\xa4rfuss K\xc3\xa4thi (kathi.barfuss)',
                          self.private_folder.Title())

    def test_Title_returns_string(self):
        self.login(self.regular_user)
        self.assertTrue(isinstance(self.private_folder.Title(), str))

    def test_uses_userid_as_reference_number_part(self):
        self.login(self.regular_user)
        self.assertEquals('P Client1 kathi-barfuss',
                          IReferenceNumber(self.private_folder).get_number())

    def test_adds_additonal_roles_after_creation(self):
        self.login(self.dossier_responsible)
        create_members_folder(self.private_root)

        folder = self.private_root.get(self.dossier_responsible.getId())
        self.assertItemsEqual(
            ['Publisher', 'Authenticated', 'Owner', 'Editor', 'Reader',
             'Contributor', 'Reviewer', 'Member'],
            api.user.get_roles(username=self.dossier_responsible.getId(), obj=folder))

    def test_handles_dashes_in_userids(self):
        create(Builder('user').with_userid('peter-mustermann'))
        create(Builder('ogds_user')
               .having(userid='peter-mustermann',
                       firstname='Peter',
                       lastname='Mustermann'))

        mtool = api.portal.get_tool('portal_membership')
        mtool.createMemberArea(member_id='peter-mustermann')

        folder = mtool.getHomeFolder(id='peter-mustermann')
        self.assertEquals(
            'Mustermann Peter (peter-mustermann)', folder.Title())


class TestPrivateFolderTabbedView(IntegrationTestCase):

    features = ('private',)

    @browsing
    def test_has_a_only_a_dossier_tab(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.private_folder)

        self.assertEquals(
            ['Dossiers'], browser.css('.formTab').text)

    @browsing
    def test_private_root_is_hidden_from_breadcrumbs(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.private_folder)

        self.assertEqual(
            [u'B\xe4rfuss K\xe4thi (kathi.barfuss)'],
            browser.css('#portal-breadcrumbs li').text)


class TestPrivateFolderTabbedViewSolr(SolrIntegrationTestCase):

    features = ('private',)

    @browsing
    def test_dossier_tab_lists_all_containig_private_dossiers(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.private_folder, view='tabbedview_view-dossiers')

        self.assertEquals(
            [['', 'Reference Number', 'Title',
              'Review state', 'Responsible', 'Start', 'End', 'Keywords'],
             ['', 'P Client1 kathi-barfuss / 2', 'Mein Dossier 2',
              'dossier-state-active', '', '31.08.2016', '', ''],
             ['', 'P Client1 kathi-barfuss / 1', 'Mein Dossier 1',
              'dossier-state-active', '', '31.08.2016', '', '']],
            browser.css('.listing').first.lists())

    @browsing
    def test_copy_and_move_items_actions_are_disabled(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.private_folder, view='tabbedview_view-dossiers')

        self.assertEquals(
            ['Delete', 'Export selection', 'Print selection (PDF)'],
            browser.css('.actionMenuContent a').text)


class TestMyRepositoryAction(IntegrationTestCase):

    features = ('private',)

    @browsing
    def is_show_when_private_folder_exists_and_redirects_to_homefolder(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open()

        self.assertIn('My Repository',
                      browser.css('#portal-globalnav li').text)

        browser.click_on('My Repository')
        self.assertEquals(self.private_folder.absolute_url(), browser.url)
