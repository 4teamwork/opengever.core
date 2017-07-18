from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.testing import FunctionalTestCase


class TestSharingOnRepositoryFolders(FunctionalTestCase):

    def setUp(self):
        super(TestSharingOnRepositoryFolders, self).setUp()
        self.grant('Administrator')
        self.repo_folder = create(Builder('repository'))

    @browsing
    def test_add_local_roles_to_user(self, browser):
        # search for test user
        browser.login().open(self.repo_folder, view='sharing')
        browser.fill({'search_term': 'test'})
        browser.css('#sharing-save-button').first.click()

        # change local roles and save
        browser.fill({'entries.role_Reviewer:records': True})
        browser.click_on('Save')

        self.assertEquals(['Changes saved.'], info_messages())
        self.assertEquals(
            (('test_user_1_', ('Owner', u'Reviewer')),),
            self.repo_folder.get_local_roles())

    @browsing
    def test_break_permission_inheritance(self, browser):
        browser.login().open(self.repo_folder, view='sharing')
        browser.fill({'Inherit permissions from higher levels': False})
        browser.click_on('Save')

        self.assertEquals(['Changes saved.'], info_messages())
        self.assertTrue(self.repo_folder.__ac_local_roles_block__)
