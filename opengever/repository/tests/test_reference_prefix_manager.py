from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.base.adapters import ReferenceNumberPrefixAdpater
from opengever.journal.tests.utils import get_journal_entry
from opengever.repository.interfaces import IDuringRepositoryDeletion
from opengever.testing import IntegrationTestCase
from plone import api
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import noLongerProvides


class TestReferencePrefixManager(IntegrationTestCase):

    def setUp(self):
        super(TestReferencePrefixManager, self).setUp()
        with self.login(self.administrator):
            # move repo1 to prefix 3 which leaves prefix 1 unused
            manager = ReferenceNumberPrefixAdpater(self.branch_repofolder)
            manager.set_number(self.leaf_repofolder, 3)

    @browsing
    def test_list_and_unlock_unused_prefixes(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.branch_repofolder, view='referenceprefix_manager')
        self.assertEquals(
            [['1', u'Vertr\xe4ge und Vereinbarungen', 'Unlock'],
             ['3', u'Vertr\xe4ge und Vereinbarungen', 'In use']],
            browser.css('#reference_prefix_manager_table').first.lists())

        browser.click_on('Unlock')
        statusmessages.assert_no_error_messages()
        statusmessages.assert_message('Reference prefix has been unlocked.')
        self.assertEquals(
            [['3', u'Vertr\xe4ge und Vereinbarungen', 'In use']],
            browser.css('#reference_prefix_manager_table').first.lists())

    def test_manager_throws_error_when_delete_request_for_used_prefix_occurs(self):
        self.login(self.administrator)
        manager = ReferenceNumberPrefixAdpater(self.branch_repofolder)
        with self.assertRaises(Exception):
            manager.free_number(19)

    @browsing
    def test_manager_handles_deleted_repositories_correctly(self, browser):
        self.login(self.administrator, browser)

        alsoProvides(self.request, IDuringRepositoryDeletion)
        api.content.delete(obj=self.leaf_repofolder)
        noLongerProvides(self.request, IDuringRepositoryDeletion)

        browser.open(self.branch_repofolder, view='referenceprefix_manager')
        self.assertEquals(
            [['1', '-- Already removed object --', 'Unlock'],
             ['3', '-- Already removed object --', 'Unlock']],
            browser.css('#reference_prefix_manager_table').first.lists())

    @browsing
    def test_manager_shows_default_message_when_no_repository_available(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.leaf_repofolder, view='referenceprefix_manager')

        self.assertEquals(
            'No nested repositorys available.',
            browser.css('#reference_prefix_manager_table tbody').first.text)

    @browsing
    def test_manager_is_hidden_from_users_without_permission(self, browser):
        self.login(self.regular_user, browser)
        with browser.expect_unauthorized():
            browser.open(self.branch_repofolder, view='referenceprefix_manager')

    @browsing
    def test_unlock_actions_are_journalized(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.branch_repofolder, view='referenceprefix_manager')
        browser.click_on('Unlock')
        statusmessages.assert_no_error_messages()

        # get last journal entry
        journal = get_journal_entry(self.repository_root, entry=-1)
        self.assertEquals(
            'Unlocked prefix 1 in fuhrung.',
            translate(journal.get('action').get('title')))

    @browsing
    def test_error_while_unlock_shows_statusmessage(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.branch_repofolder,
                     view='referenceprefix_manager?prefix=3')
        statusmessages.assert_message(
            'The reference you try to unlock is still in use.')
