from datetime import datetime
from ftw.testing import freeze
from opengever.base.date_time import utcnow_tz_aware
from opengever.testing import IntegrationTestCase
from opengever.workspace.participation.storage import IInvitationStorage
from operator import itemgetter
from plone.uuid.interfaces import IUUID
from zope.component import getUtility
import pytz


class TestWorspaceParticipationStorage(IntegrationTestCase):

    def test_add_and_retrieve_invitation(self):
        self.login(self.workspace_admin)
        creation_date = datetime(2017, 1, 1, 1, 11, tzinfo=pytz.UTC)
        with freeze(creation_date):
            iid = getUtility(IInvitationStorage).add_invitation(
                self.workspace,
                self.workspace_guest.getId(),
                self.workspace_owner.getId(),
                'WorkspaceGuest')

        self.assertDictEqual(
            {'iid': iid,
             'target_uuid': IUUID(self.workspace),
             'recipient': 'hans.peter',
             'inviter': 'gunther.frohlich',
             'role': 'WorkspaceGuest',
             'created': creation_date,
             'updated': None},
            getUtility(IInvitationStorage).get_invitation(iid))

    def test_remove_invitation(self):
        self.login(self.workspace_admin)
        iid = self.add_invitation()

        self.assertTrue(getUtility(IInvitationStorage).get_invitation(iid))
        getUtility(IInvitationStorage).remove_invitation(iid)

        with self.assertRaises(KeyError):
            getUtility(IInvitationStorage).get_invitation(iid)

        with self.assertRaises(KeyError):
            getUtility(IInvitationStorage).remove_invitation(iid)

    def test_update_invitation(self):
        self.login(self.workspace_admin)
        storage = getUtility(IInvitationStorage)
        creation_date = datetime(2017, 1, 1, 1, 1, tzinfo=pytz.UTC)
        with freeze(creation_date) as clock:
            iid = self.add_invitation()

            self.assertDictEqual(
                {'iid': iid,
                 'target_uuid': IUUID(self.workspace),
                 'recipient': 'hans.peter',
                 'inviter': 'gunther.frohlich',
                 'role': 'WorkspaceGuest',
                 'created': creation_date,
                 'updated': None},
                storage.get_invitation(iid))

            clock.forward(hours=1)
            storage.update_invitation(iid, role='WorkspaceMember')
            self.assertDictEqual(
                {'iid': iid,
                 'target_uuid': IUUID(self.workspace),
                 'recipient': 'hans.peter',
                 'inviter': 'gunther.frohlich',
                 'role': 'WorkspaceMember',
                 'created': creation_date,
                 'updated': utcnow_tz_aware()},
                storage.get_invitation(iid))

            clock.forward(hours=1)
            storage.update_invitation(iid, recipient='fritz', inviter='hans')
            self.assertDictEqual(
                {'iid': iid,
                 'target_uuid': IUUID(self.workspace),
                 'recipient': 'fritz',
                 'inviter': 'hans',
                 'role': 'WorkspaceMember',
                 'created': creation_date,
                 'updated': utcnow_tz_aware()},
                storage.get_invitation(iid))

            clock.forward(hours=1)
            storage.update_invitation(iid, target=self.workspace_folder)
            self.assertDictEqual(
                {'iid': iid,
                 'target_uuid': IUUID(self.workspace_folder),
                 'recipient': 'fritz',
                 'inviter': 'hans',
                 'role': 'WorkspaceMember',
                 'created': creation_date,
                 'updated': utcnow_tz_aware()},
                storage.get_invitation(iid))

            with self.assertRaises(KeyError):
                storage.update_invitation(iid, target_uuid='new')

            with self.assertRaises(KeyError):
                storage.update_invitation(iid, created='new')

            with self.assertRaises(KeyError):
                storage.update_invitation(iid, updated='new')

    def test_iter_invitations_for_context(self):
        self.login(self.workspace_admin)
        storage = getUtility(IInvitationStorage)
        workspace1 = self.add_invitation(target=self.workspace)
        workspace2 = self.add_invitation(target=self.workspace)
        folder = self.add_invitation(target=self.workspace_folder)

        self.assertItemsEqual(
            [workspace1, workspace2],
            map(itemgetter('iid'), storage.iter_invitations_for_context(self.workspace)))

        self.assertItemsEqual(
            [folder],
            map(itemgetter('iid'), storage.iter_invitations_for_context(self.workspace_folder)))

    def test_iter_invitations_for_recipient(self):
        self.login(self.workspace_admin)
        storage = getUtility(IInvitationStorage)
        foo1 = self.add_invitation(recipient='foo')
        foo2 = self.add_invitation(recipient='foo')
        bar = self.add_invitation(recipient='bar')

        self.assertItemsEqual(
            [foo1, foo2],
            map(itemgetter('iid'), storage.iter_invitations_for_recipient('foo')))

        self.assertItemsEqual(
            [bar],
            map(itemgetter('iid'), storage.iter_invitations_for_recipient('bar')))

    def test_iter_invitations_for_inviter(self):
        self.login(self.workspace_admin)
        storage = getUtility(IInvitationStorage)
        foo1 = self.add_invitation(inviter='foo')
        foo2 = self.add_invitation(inviter='foo')
        bar = self.add_invitation(inviter='bar')

        self.assertItemsEqual(
            [foo1, foo2],
            map(itemgetter('iid'), storage.iter_invitations_for_inviter('foo')))

        self.assertItemsEqual(
            [bar],
            map(itemgetter('iid'), storage.iter_invitations_for_inviter('bar')))

    def add_invitation(self, **options):
        options.setdefault('target', self.workspace)
        options.setdefault('recipient', self.workspace_guest.getId())
        options.setdefault('inviter', self.workspace_owner.getId())
        options.setdefault('role', 'WorkspaceGuest')
        return getUtility(IInvitationStorage).add_invitation(**options)
