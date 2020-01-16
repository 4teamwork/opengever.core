from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
import json


class TestRolesVocabulary(IntegrationTestCase):

    def test_roles_vocabulary_list_all_managed_roles(self):
        self.login(self.workspace_owner)
        factory = getUtility(IVocabularyFactory,
                             name='opengever.workspace.RolesVocabulary')
        self.assertItemsEqual(
            ['Admin', 'Member', 'Guest'],
            [term.title for term in factory(context=self.portal)])


class TestPossibleWorkspaceFolderParticipantsVocabulary(IntegrationTestCase):

    def test_vocabulary_lists_an_empty_list_if_not_on_a_folder(self):
        self.login(self.workspace_owner)
        factory = getUtility(IVocabularyFactory,
                             name='opengever.workspace.PossibleWorkspaceFolderParticipantsVocabulary')
        self.assertItemsEqual(
            [],
            [term.token for term in factory(context=self.workspace)])

    @browsing
    def test_vocabulary_returns_a_list_of_possible_participants(self, browser):
        self.login(self.workspace_admin, browser)

        # Only the workspace admin will be participating on the workspace folder
        # after blocking role inheritance without copying the roles.
        browser.open(
            self.workspace_folder,
            view='/@role-inheritance',
            data=json.dumps({'blocked': True, 'copy_roles': False}),
            method='POST',
            headers=self.api_headers)

        factory = getUtility(IVocabularyFactory,
                             name='opengever.workspace.PossibleWorkspaceFolderParticipantsVocabulary')

        self.assertItemsEqual(
            [self.workspace_member.id, self.workspace_owner.id, self.workspace_guest.id],
            [term.token for term in factory(context=self.workspace_folder)],
            "The vocabulary should return only the possible participants, not "
            "all. The workspace admin is already a member of the current "
            "folder. It should be excluded")
