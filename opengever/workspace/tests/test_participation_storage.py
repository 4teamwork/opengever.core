from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import freeze
from opengever.base.date_time import utcnow_tz_aware
from opengever.testing import IntegrationTestCase
from opengever.workspace.exceptions import DuplicatePendingInvitation
from opengever.workspace.exceptions import MultipleUsersFound
from opengever.workspace.participation.storage import IInvitationStorage
from opengever.workspace.participation.storage import STATE_ACCEPTED
from opengever.workspace.participation.storage import STATE_DECLINED
from opengever.workspace.participation.storage import STATE_PENDING
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
                self.workspace_guest.getProperty('email'),
                self.workspace_owner.getId(),
                'WorkspaceGuest')

        self.assertDictEqual(
            {'iid': iid,
             'target_uuid': IUUID(self.workspace),
             'recipient': 'hans.peter',
             'recipient_email': 'hans.peter@gever.local',
             'inviter': 'gunther.frohlich',
             'role': 'WorkspaceGuest',
             'comment': u'',
             'created': creation_date,
             'status': 'pending',
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

    def test_mark_invitation_as_accepted(self):
        self.login(self.workspace_admin)
        storage = getUtility(IInvitationStorage)
        iid = self.add_invitation()
        self.assertEqual(STATE_PENDING, storage.get_invitation(iid)['status'])

        storage.mark_invitation_as_accepted(iid)
        self.assertEqual(STATE_ACCEPTED, storage.get_invitation(iid)['status'])

    def test_mark_invitation_as_declined(self):
        self.login(self.workspace_admin)
        storage = getUtility(IInvitationStorage)
        iid = self.add_invitation()
        self.assertEqual(STATE_PENDING, storage.get_invitation(iid)['status'])

        storage.mark_invitation_as_declined(iid)
        self.assertEqual(STATE_DECLINED, storage.get_invitation(iid)['status'])

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
                 'recipient_email': 'hans.peter@gever.local',
                 'inviter': 'gunther.frohlich',
                 'role': 'WorkspaceGuest',
                 'comment': u'',
                 'created': creation_date,
                 'updated': None,
                 'status': 'pending'},
                storage.get_invitation(iid))

            clock.forward(hours=1)
            storage.update_invitation(iid, role='WorkspaceMember')
            self.assertDictEqual(
                {'iid': iid,
                 'target_uuid': IUUID(self.workspace),
                 'recipient': 'hans.peter',
                 'recipient_email': 'hans.peter@gever.local',
                 'inviter': 'gunther.frohlich',
                 'role': 'WorkspaceMember',
                 'comment': u'',
                 'created': creation_date,
                 'updated': utcnow_tz_aware(),
                 'status': 'pending'},
                storage.get_invitation(iid))

            clock.forward(hours=1)
            storage.update_invitation(iid, recipient='fritz',
                                      inviter='hans', comment=u"new")
            self.assertDictEqual(
                {'iid': iid,
                 'target_uuid': IUUID(self.workspace),
                 'recipient': 'fritz',
                 'recipient_email': 'hans.peter@gever.local',
                 'inviter': 'hans',
                 'role': 'WorkspaceMember',
                 'comment': u'new',
                 'created': creation_date,
                 'updated': utcnow_tz_aware(),
                 'status': 'pending'},
                storage.get_invitation(iid))

            clock.forward(hours=1)
            storage.update_invitation(iid, target=self.workspace_folder)
            self.assertDictEqual(
                {'iid': iid,
                 'target_uuid': IUUID(self.workspace_folder),
                 'recipient': 'fritz',
                 'recipient_email': 'hans.peter@gever.local',
                 'inviter': 'hans',
                 'role': 'WorkspaceMember',
                 'comment': u'new',
                 'created': creation_date,
                 'updated': utcnow_tz_aware(),
                 'status': 'pending'},
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
        workspace2 = self.add_invitation(target=self.workspace,
                                         recipient_email='foo@example.com')
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
        foo1 = self.add_invitation(recipient_email='foo@example.com')
        foo2 = self.add_invitation(target=self.workspace_folder,
                                   recipient_email='foo@example.com')
        qux = self.add_invitation(recipient_email='qux@example.com')

        self.assertItemsEqual(
            [foo1, foo2],
            map(itemgetter('iid'),
                storage.iter_invitations_for_recipient_email('foo@example.com')))
        self.assertItemsEqual(
            [qux],
            map(itemgetter('iid'),
                storage.iter_invitations_for_recipient_email('qux@example.com')))

    def test_iter_invitations_for_inviter(self):
        self.login(self.workspace_admin)
        storage = getUtility(IInvitationStorage)
        foo1 = self.add_invitation(inviter='foo')
        foo2 = self.add_invitation(inviter='foo', recipient_email='foo@example.com')
        bar = self.add_invitation(inviter='bar', recipient_email='qux@example.com')

        self.assertItemsEqual(
            [foo1, foo2],
            map(itemgetter('iid'), storage.iter_invitations_for_inviter('foo')))

        self.assertItemsEqual(
            [bar],
            map(itemgetter('iid'), storage.iter_invitations_for_inviter('bar')))

    def test_iter_invitations_for_current_user_lists_only_pending_invitations(self):
        self.login(self.workspace_admin)
        storage = getUtility(IInvitationStorage)
        iid1 = self.add_invitation()
        iid2 = self.add_invitation(target=self.workspace_folder)

        self.login(self.workspace_guest)
        self.assertItemsEqual(
            [iid1, iid2],
            map(itemgetter('iid'), storage.iter_invitations_for_current_user()))

        storage.mark_invitation_as_accepted(iid1)
        self.assertItemsEqual(
            [iid2],
            map(itemgetter('iid'), storage.iter_invitations_for_current_user()))

        storage.mark_invitation_as_declined(iid2)
        self.assertItemsEqual(
            [],
            map(itemgetter('iid'), storage.iter_invitations_for_current_user()))

    def test_iter_invitations_for_current_user_lists_matching_mail_and_userid(self):
        self.login(self.workspace_admin)
        storage = getUtility(IInvitationStorage)
        iid1 = self.add_invitation()
        iid2 = self.add_invitation(target=self.workspace_folder)

        storage._write_invitations[iid1]['recipient'] = None
        storage._write_invitations[iid2]['recipient_email'] = None

        self.login(self.workspace_guest)
        self.assertItemsEqual(
            [iid1, iid2],
            map(itemgetter('iid'), storage.iter_invitations_for_current_user()))

    def test_map_email_to_current_userid_for_all_invitations(self):
        self.login(self.workspace_admin)
        storage = getUtility(IInvitationStorage)
        iid1 = self.add_invitation()
        iid2 = self.add_invitation(recipient_email=self.workspace_admin.getProperty('email'))

        self.login(self.workspace_guest)
        self.assertItemsEqual(
            [iid1],
            map(itemgetter('iid'), storage.iter_invitations_for_current_user()))

        storage.map_email_to_current_userid_for_all_invitations(
            self.workspace_admin.getProperty('email'))

        self.assertItemsEqual(
            [iid1, iid2],
            map(itemgetter('iid'), storage.iter_invitations_for_current_user()))

    def test_prevents_duplicate_invitation_per_workspace(self):
        self.login(self.workspace_admin)

        getUtility(IInvitationStorage).add_invitation(
            self.workspace,
            'foo@example.com',
            self.workspace_owner.getId(),
            'WorkspaceGuest')

        with self.assertRaises(DuplicatePendingInvitation):
            getUtility(IInvitationStorage).add_invitation(
                        self.workspace,
                        'foo@example.com',
                        self.workspace_owner.getId(),
                        'WorkspaceGuest')

    def test_raises_when_multiple_users_have_same_email(self):
        with self.login(self.manager):
            create(Builder('user')
                   .named('foo', 'bar')
                   .with_roles(['Member'])
                   .in_groups('fa_users')
                   .with_email('twice@example.com'))

            create(Builder('user')
                   .named('bar', 'qux')
                   .with_roles(['Member'])
                   .in_groups('fa_users')
                   .with_email('twice@example.com'))

        self.login(self.workspace_admin)
        with self.assertRaises(MultipleUsersFound):
            getUtility(IInvitationStorage).add_invitation(
                        self.workspace,
                        'twice@example.com',
                        self.workspace_owner.getId(),
                        'WorkspaceGuest')

    def add_invitation(self, **options):
        options.setdefault('target', self.workspace)
        options.setdefault('recipient_email', self.workspace_guest.getProperty('email'))
        options.setdefault('inviter', self.workspace_owner.getId())
        options.setdefault('role', 'WorkspaceGuest')
        return getUtility(IInvitationStorage).add_invitation(**options)
