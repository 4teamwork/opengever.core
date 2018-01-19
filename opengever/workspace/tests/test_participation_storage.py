from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from opengever.testing import IntegrationTestCase
from opengever.workspace.participation.invitation import Invitation
from opengever.workspace.participation.storage import InvitationStorage
from opengever.workspace.participation.storage import STORAGE_CACHE_KEY
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAnnotations


class TestWorspaceParticipationStorage(IntegrationTestCase):

    def setUp(self):
        super(TestWorspaceParticipationStorage, self).setUp()
        self.login(self.workspace_admin)
        self.storage = InvitationStorage(self.workspace)

    def test_cached_access_of_invitations(self):
        self.assertNotIn(STORAGE_CACHE_KEY, dir(self.storage))
        # Not write on read!!
        self.storage.invitations
        self.assertNotIn(STORAGE_CACHE_KEY, dir(self.storage))

        self.storage.initialize_storage()
        self.storage.invitations
        self.assertIn(STORAGE_CACHE_KEY, dir(self.storage))

    def test_not_inititalize_storage_is_none(self):
        self.assertEquals({}, self.storage.invitations)
        self.assertNotIn(self.storage.ANNOTATIONS_DATA_KEY,
                         IAnnotations(self.workspace))

    def test_inititalized_storage_is_a_persisten_dict(self):
        self.storage.initialize_storage()
        self.assertTrue(isinstance(self.storage.invitations, PersistentDict),
                        'Expect a PersistentDict in storage')

    def test_get_used_iids_is_always_unique(self):
        invitation = Invitation(self.workspace, self.regular_user.getId(),
                                self.workspace_admin.getId(), 'WorkspacesUser')

        self.assertNotEquals(self.storage.generate_iid_for(invitation),
                             self.storage.generate_iid_for(invitation))

        with freeze(datetime(2017, 1, 1, 1, 11)):
            self.assertEquals('1e05daca75db263c91482337f3819ead',
                              self.storage.generate_iid_for(invitation))

    def test_get_used_iids(self):
        invitation1 = Invitation(self.workspace, self.regular_user.getId(),
                                 self.workspace_admin.getId(), 'WorkspacesUser')
        invitation2 = Invitation(self.workspace, self.regular_user.getId(),
                                 self.workspace_admin.getId(), 'WorkspacesUser')
        self.assertItemsEqual([invitation1.iid, invitation2.iid],
                              self.storage.get_used_iids().keys())

    def test_add_first_invitation(self):
        invitation = Invitation(self.workspace, self.regular_user.getId(),
                                self.workspace_admin.getId(), 'WorkspacesUser')

        self.storage.add_invitation(invitation)

        self.assertEquals(
            1, len(self.storage.invitations), 'Expect 1 item in storage')

        self.assertEquals(
            1, len(self.storage.invitations[self.regular_user.getId()]),
            'Expect 1 invitation in storage')

    def test_add_multiple_invitation_to_one_user(self):
        invitation = Invitation(self.workspace, self.regular_user.getId(),
                                self.workspace_admin.getId(), 'WorkspacesUser')
        self.storage.add_invitation(invitation)

        workspace2 = create(Builder('workspace')
                            .within(self.workspace_root)
                            .titled(u'Second workspace'))

        invitation = Invitation(workspace2, self.regular_user.getId(),
                                self.workspace_admin.getId(), 'WorkspacesUser')
        self.storage.add_invitation(invitation)

        self.assertEquals(
            2, len(self.storage.invitations[self.regular_user.getId()]),
            'Expect 2 invitations')

    def test_get_invitation_by_iid(self):
        invitation = Invitation(self.workspace, self.regular_user.getId(),
                                self.workspace_admin.getId(), 'WorkspacesUser')
        self.storage.add_invitation(invitation)

        self.assertEquals(invitation,
                          self.storage.get_invitation_by_iid(invitation.iid))

        self.assertIsNone(self.storage.get_invitation_by_iid('asdf'),
                          'Should be None, if not invitation is found.')

    def test_get_invitations_by_userid(self):
        invitation = Invitation(self.workspace, self.regular_user.getId(),
                                self.workspace_admin.getId(), 'WorkspacesUser')
        self.storage.add_invitation(invitation)

        self.assertItemsEqual(
            [invitation],
            self.storage.get_invitations_by_userid(self.regular_user.getId()))

        self.assertEquals(
            [],
            self.storage.get_invitations_by_userid('someuserid'),
            'Should be a empty, if not invitation is found.')

        self.login(self.regular_user)
        self.assertItemsEqual([invitation],
                              self.storage.get_invitations_by_userid())

    def test_get_invitations_invited_by(self):
        invitation = Invitation(self.workspace, self.regular_user.getId(),
                                self.workspace_admin.getId(), 'WorkspacesUser')
        self.storage.add_invitation(invitation)

        workspace2 = create(Builder('workspace')
                            .within(self.workspace_root)
                            .titled(u'Second workspace'))
        invitation2 = Invitation(workspace2, self.regular_user.getId(),
                                 self.workspace_admin.getId(), 'WorkspacesUser')
        self.storage.add_invitation(invitation2)

        self.assertItemsEqual(
            [invitation, invitation2],
            self.storage.get_invitations_invited_by(self.workspace_admin.getId()))

        self.assertEquals(
            [],
            self.storage.get_invitations_invited_by('someuserid'))

        self.login(self.regular_user)
        self.assertItemsEqual([], self.storage.get_invitations_invited_by())

        self.login(self.workspace_admin)
        self.assertItemsEqual(
            [invitation, invitation2],
            self.storage.get_invitations_invited_by())

    def test_get_invitations_for_context(self):
        invitation = Invitation(self.workspace, self.regular_user.getId(),
                                self.workspace_admin.getId(), 'WorkspacesUser')
        invitation2 = Invitation(self.workspace, self.regular_user.getId(),
                                 self.workspace_admin.getId(), 'WorkspacesUser')

        self.storage.add_invitation(invitation)
        self.storage.add_invitation(invitation2)

        workspace2 = create(Builder('workspace')
                            .within(self.workspace_root)
                            .titled(u'Second workspace'))
        invitation3 = Invitation(workspace2, self.regular_user.getId(),
                                 self.workspace_admin.getId(), 'WorkspacesUser')
        self.storage.add_invitation(invitation3)

        self.assertItemsEqual(
            [invitation, invitation2],
            self.storage.get_invitations_for_context(self.workspace))

        self.assertItemsEqual(
            [invitation3],
            self.storage.get_invitations_for_context(workspace2))

        self.assertEquals(
            [],
            self.storage.get_invitations_for_context(self.dossier))

    def test_remove_invitation(self):
        invitation = Invitation(self.workspace, self.regular_user.getId(),
                                self.workspace_admin.getId(), 'WorkspacesUser')

        self.storage.add_invitation(invitation)
        self.assertTrue(self.storage.remove_invitation(invitation),
                        'Invitation should be removed')
        self.assertFalse(self.storage.remove_invitation(invitation),
                         'Invitation has been already removed')
