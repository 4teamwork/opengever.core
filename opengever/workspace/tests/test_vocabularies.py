from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.role_assignments import ASSIGNMENT_VIA_SHARING
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.base.role_assignments import SharingRoleAssignment
from opengever.testing import IntegrationTestCase
from plone import api
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


class TestWorkspaceContentMembersVocabulary(IntegrationTestCase):

    def test_vocabulary_list_all_members_of_the_current_workspace(self):
        self.login(self.workspace_member)
        factory = getUtility(IVocabularyFactory,
                             name='opengever.workspace.WorkspaceContentMembersVocabulary')

        # Workspace 1
        self.assertItemsEqual(
            [self.workspace_guest.id, self.workspace_member.id, self.workspace_owner.id, self.workspace_admin.id],
            [term.token for term in factory(context=self.workspace)])

        # Workspace 2
        workspace2 = create(Builder('workspace').within(self.workspace_root))
        self.assertItemsEqual(
            [self.workspace_member.id],
            [term.token for term in factory(context=workspace2)])

    def test_vocabulary_respects_local_roles_block(self):
        self.login(self.workspace_member)
        factory = getUtility(IVocabularyFactory,
                             name='opengever.workspace.WorkspaceContentMembersVocabulary')

        self.assertItemsEqual(
            [self.workspace_guest.id, self.workspace_member.id,
             self.workspace_owner.id, self.workspace_admin.id],
            [term.token for term in factory(context=self.workspace_folder)])

        self.workspace_folder.__ac_local_roles_block__ = True
        RoleAssignmentManager(self.workspace_folder).add_or_update_assignment(
            SharingRoleAssignment(api.user.get_current().getId(), ['WorkspaceMember']))

        self.assertItemsEqual(
            [self.workspace_member.id],
            [term.token for term in factory(context=self.workspace_folder)])

    def test_meeting_attendees_persist_after_user_role_removal(self):
        self.login(self.workspace_admin)

        workspace = create(Builder('workspace').titled(u'Project A').within(self.workspace_root))
        self.set_roles(workspace, self.workspace_admin.getId(), ['WorkspaceMember'])
        self.set_roles(workspace, self.workspace_guest.getId(), ['WorkspaceGuest'])
        self.set_roles(workspace, self.workspace_member.getId(), ['WorkspaceMember'])

        factory = getUtility(IVocabularyFactory,
                             name='opengever.workspace.WorkspaceContentMembersVocabulary')

        create(
            Builder('workspace meeting')
            .within(workspace)
            .titled(u'Besprechung Kl\xe4ranlage')
            .having(responsible=self.workspace_member.getId())
            .having(attendees=[
                self.workspace_admin.getId(), self.workspace_guest.getId(), self.workspace_member.getId()])
        )

        # Verify initial attendees
        self.assertSequenceEqual(
            [self.workspace_admin.getId(), self.workspace_guest.getId(), self.workspace_member.getId()],
            [term.token for term in factory(context=workspace)]
        )

        # Remove users Roles
        role_assignment_manager = RoleAssignmentManager(workspace)
        role_assignment_manager.clear_by_cause_and_principal(ASSIGNMENT_VIA_SHARING, self.workspace_member.getId())
        role_assignment_manager.clear_by_cause_and_principal(ASSIGNMENT_VIA_SHARING, self.workspace_guest.getId())

        # Verify that the users' roles are removed in the workspace
        self.assertEqual(
            [self.workspace_admin.getId()], [term.token for term in factory(context=workspace)])

        # Verify that the participants are still displayed in the meeting
        self.assertEquals(
            self.workspace_member.getId(),
            factory(context=workspace).getTerm(self.workspace_member.getId()).token)

        self.assertEquals(
            self.workspace_guest.getId(),
            factory(context=workspace).getTerm(self.workspace_guest.getId()).token)
