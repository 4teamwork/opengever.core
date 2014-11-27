from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import assert_message
from opengever.repository.deleter import RepositoryDeleter
from opengever.testing import FunctionalTestCase
from plone import api
from zExceptions import Unauthorized


class TestRepositoryDeleter(FunctionalTestCase):

    def setUp(self):
        super(TestRepositoryDeleter, self).setUp()

        self.repository_root = create(Builder('repository_root'))
        self.repository = create(Builder('repository')
                                 .within(self.repository_root))

        self.grant('Administrator')

    def test_deletion_is_not_allowed_when_repository_is_not_empty(self):
        create(Builder('dossier').within(self.repository))
        deleter = RepositoryDeleter(self.repository)

        self.assertFalse(deleter.is_deletion_allowed())

    def test_deletion_is_allowed_when_repository_is_empty(self):
        deleter = RepositoryDeleter(self.repository)

        self.assertTrue(deleter.is_deletion_allowed())

    def test_repository_deletion(self):
        deleter = RepositoryDeleter(self.repository)
        deleter.delete()

        self.assertEquals([], self.repository_root.listFolderContents())

    def test_repository_deletion_raises_unauthorized_when_preconditions_not_satisfied(self):
        create(Builder('dossier').within(self.repository))
        deleter = RepositoryDeleter(self.repository)

        with self.assertRaises(Unauthorized):
            deleter.delete()


class TestRepositoryDeletion(FunctionalTestCase):

    def setUp(self):
        super(TestRepositoryDeletion, self).setUp()

        self.repository_root = create(Builder('repository_root'))
        self.repository = create(Builder('repository')
                                 .within(self.repository_root))

        self.grant('Administrator')

    @browsing
    def test_deletion_is_only_be_possible_with_admin_or_manager_role(self, browser):
        acl_users = api.portal.get_tool('acl_users')
        valid_roles = list(acl_users.portal_role_manager.valid_roles())
        valid_roles.remove('Administrator')
        valid_roles.remove('Manager')
        self.grant(*valid_roles)

        with self.assertRaises(Unauthorized):
            api.content.delete(obj=self.repository)

    @browsing
    def test_delete_action_is_not_available_when_preconditions_not_satisfied(self, browser):
        create(Builder('dossier').within(self.repository))
        browser.login().open(self.repository)
        self.assertEquals(
            ['Prefix Manager',
             'Properties',
             'Sharing',
             'repositoryfolder-transition-inactivate'],
            browser.css('#plone-contentmenu-actions .actionMenuContent a').text)

    @browsing
    def test_delete_action_is_available_when_preconditions_satisfied(self, browser):
        browser.login().open(self.repository)
        self.assertEquals(
            ['Delete',
             'Prefix Manager',
             'Properties',
             'Sharing',
             'repositoryfolder-transition-inactivate'],
            browser.css('#plone-contentmenu-actions .actionMenuContent a').text)

    @browsing
    def test_raise_unauthorized_when_preconditions_not_satisfied(self, browser):
        create(Builder('dossier').within(self.repository))
        with self.assertRaises(Unauthorized):
            browser.login().open(self.repository, view='delete_repository')

    @browsing
    def test_cancel_redirects_back_to_repository(self, browser):
        browser.login().open(self.repository, view='delete_repository')
        browser.css('#form-buttons-cancel').first.click()

        self.assertEquals(self.repository.absolute_url(), browser.url)

    @browsing
    def test_submit_redirects_to_parent(self, browser):
        browser.login().open(self.repository, view='delete_repository')
        browser.css('#form-buttons-delete').first.click()

        self.assertEquals(self.repository_root.absolute_url(), browser.url)
        assert_message("The repository have been successfully deleted.")

    @browsing
    def test_form_is_csrf_safe(self, browser):
        url = '{}/delete_repository?form.buttons.delete=true'.format(
            self.repository.absolute_url())

        with self.assertRaises(Unauthorized):
            browser.login().open(url)
