from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages import statusmessages
from opengever.repository.deleter import RepositoryDeleter
from opengever.testing import IntegrationTestCase
from plone import api
from zExceptions import Unauthorized


class TestRepositoryDeleter(IntegrationTestCase):

    @browsing
    def test_deletion_is_only_allowed_through_deleter(self, browser):
        self.login(self.manager, browser)
        repo_physical_path = self.empty_repofolder.getPhysicalPath()

        browser.open(self.empty_repofolder, view='delete_confirmation')

        with browser.expect_http_error(code=403, reason='Forbidden'):
            browser.click_on("Delete")

        with self.observe_children(self.repository_root) as children:
            browser.open(self.empty_repofolder, view='delete_repository')
            browser.click_on("Delete")
        self.assertEqual(1, len(children["removed"]))
        removed = children["removed"].pop()
        self.assertEqual(repo_physical_path, removed.getPhysicalPath())

    def test_deletion_is_not_allowed_when_repository_is_not_empty(self):
        self.login(self.administrator)
        self.assertTrue(self.branch_repofolder.objectIds(),
                        'Precondition: Assumed repofolder to have children.')
        self.assertFalse(RepositoryDeleter(self.branch_repofolder)
                         .is_deletion_allowed())

    def test_deletion_is_allowed_when_repository_is_empty(self):
        self.login(self.administrator)
        self.assertFalse(self.empty_repofolder.objectIds(),
                         'Precondition: Assumed repofolder to have no children.')
        self.assertTrue(RepositoryDeleter(self.empty_repofolder)
                        .is_deletion_allowed())

    def test_repository_deletion(self):
        self.login(self.administrator)
        parent = aq_parent(aq_inner(self.empty_repofolder))
        repo_id = self.empty_repofolder.getId()

        self.assertIn(repo_id, parent.objectIds())
        RepositoryDeleter(self.empty_repofolder).delete()
        self.assertNotIn(repo_id, parent.objectIds())

    def test_deletion_denied_without_admin_or_manager_role(self):
        acl_users = api.portal.get_tool('acl_users')
        valid_roles = list(acl_users.portal_role_manager.valid_roles())
        valid_roles.remove('Administrator')
        valid_roles.remove('Manager')

        user = create(Builder('user').with_roles(*valid_roles))
        self.login(user)
        with self.assertRaises(Unauthorized):
            api.content.delete(obj=self.empty_repofolder)

    @browsing
    def test_delete_action_is_only_available_when_preconditions_satisfied(
            self, browser):
        self.login(self.administrator, browser)
        browser.open(self.empty_repofolder)
        self.assertIn(
            'Delete',
            editbar.menu_options("Actions"),
            'Expected "Delete" action to be visible on {!r}.'.format(
                self.empty_repofolder))

        browser.open(self.branch_repofolder)
        self.assertNotIn(
            'Delete',
            editbar.menu_options("Actions"),
            'Expected "Delete" action to be invisible on {!r}.'.format(
                self.branch_repofolder))

        browser.open(self.leaf_repofolder)
        self.assertNotIn(
            'Delete',
            editbar.menu_options("Actions"),
            'Expected "Delete" action to be invisible on {!r}.'.format(
                self.branch_repofolder))

    @browsing
    def test_delete_action_is_only_available_when_preconditions_satisfied_also_for_managers(
            self, browser):
        self.login(self.manager, browser)

        browser.open(self.empty_repofolder)
        self.assertIn(
            'Delete',
            editbar.menu_options("Actions"),
            'Expected "Delete" action to be visible on {!r}.'.format(
                self.empty_repofolder))

        browser.open(self.branch_repofolder)
        self.assertNotIn(
            'Delete',
            editbar.menu_options("Actions"),
            'Expected "Delete" action to be invisible on {!r}.'.format(
                self.branch_repofolder))

        browser.open(self.leaf_repofolder)
        self.assertNotIn(
            'Delete',
            editbar.menu_options("Actions"),
            'Expected "Delete" action to be invisible on {!r}.'.format(
                self.branch_repofolder))

    @browsing
    def test_raise_unauthorized_when_preconditions_not_satisfied(self, browser):
        self.login(self.administrator, browser)
        # This causes an infinite redirection loop between ++add++ and
        # reqiure_login. By enabling exception_bubbling we can catch the
        # Unauthorized exception and end the infinite loop.
        browser.exception_bubbling = True
        with self.assertRaises(Unauthorized):
            browser.open(self.branch_repofolder, view='delete_repository')

    @browsing
    def test_cancel_redirects_back_to_repository(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.empty_repofolder, view='delete_repository')
        browser.click_on('Cancel')
        self.assertEquals(self.empty_repofolder, browser.context)

    @browsing
    def test_submit_redirects_to_parent(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.empty_repofolder, view='delete_repository')
        browser.click_on('Delete')
        statusmessages.assert_message(
            'The repository have been successfully deleted.')
        self.assertEquals(self.repository_root, browser.context)

    @browsing
    def test_form_is_csrf_safe(self, browser):
        self.login(self.administrator, browser)
        url = '{}/delete_repository?form.buttons.delete=true'.format(
            self.empty_repofolder.absolute_url())

        with browser.expect_unauthorized():
            browser.open(url)
