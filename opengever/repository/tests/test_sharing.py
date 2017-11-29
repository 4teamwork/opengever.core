from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.testing import IntegrationTestCase


class TestSharingOnRepositoryFolders(IntegrationTestCase):

    @browsing
    def test_add_local_roles_to_user(self, browser):
        # because of how form fill works combined with the testbrowser
        # boxes that were already checked for on user will get checked
        # for all the others when submitting the form. We therefore block
        # permission inheritance on branch_repofolder then test the local
        # roleaddition in the leaf_repofolder, to be sure we have a clean
        # sheet.
        self.login(self.administrator, browser)
        self.branch_repofolder.__ac_local_roles_block__ = True
        browser.open(self.leaf_repofolder, view='sharing')
        self.assert_local_roles(
            tuple(), self.regular_user.getId(), self.leaf_repofolder)
        browser.fill({'search_term': self.regular_user.getId()})
        browser.css('#sharing-save-button').first.click()
        browser.fill({'entries.role_Reader:records': True})
        browser.click_on('Save')
        self.assert_local_roles(
            (u'Reader',), self.regular_user.getId(), self.leaf_repofolder)

    @browsing
    def test_break_permission_inheritance(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.branch_repofolder, view='sharing')
        browser.fill({'Inherit permissions from higher levels': False})
        browser.click_on('Save')

        self.assertEquals(['Changes saved.'], info_messages())
        self.assertTrue(self.branch_repofolder.__ac_local_roles_block__)
