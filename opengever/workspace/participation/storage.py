from BTrees.OOBTree import OOBTree
from opengever.base.date_time import utcnow_tz_aware
from opengever.workspace.exceptions import DuplicatePendingInvitation
from opengever.workspace.exceptions import MultipleUsersFound
from opengever.workspace.participation.invitation_mailer import InvitationMailer
from persistent.mapping import PersistentMapping
from plone import api
from plone.uuid.interfaces import IUUID
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.interface import Interface
import uuid


class IInvitationStorage(Interface):
    pass


STATE_PENDING = 'pending'


@implementer(IInvitationStorage)
class InvitationStorage(object):
    """The invitation stores and manages the invitation. All modification in
    the list of invitations (appending new invitations, deleting existing
    invitations, etc.) should be done through the invitation storage.
    The invitation storage is a utility.
    The storage stores its data into annotations on the plone site root.
    """

    ANNOTATIONS_DATA_KEY = 'opengever.workspace : invitations'

    @property
    def portal_annotations(self):
        """The annotations of the plone site root
        """
        return IAnnotations(getSite())

    def add_invitation(self, target, recipient_email, inviter, role, comment=u''):
        if self._has_pending_invitation(target, recipient_email):
            raise DuplicatePendingInvitation(
                'Duplicate pending invitation for {}'.format(recipient_email))

        iid = self._generate_iid()
        recipient_user_id = self._find_user_id_for_email(recipient_email)

        self._write_invitations[iid] = PersistentMapping({
            'iid': iid,
            'target_uuid': IUUID(target),
            'recipient': recipient_user_id,
            'recipient_email': recipient_email,
            'inviter': inviter,
            'role': role,
            'comment': comment,
            'created': utcnow_tz_aware(),
            'updated': None,
            'status': STATE_PENDING})
        self.send_invitation_mail(iid)
        return iid

    def get_invitation(self, iid):
        # The invitation is read-only.
        data = dict(self._read_invitations[iid])
        return data

    def remove_invitation(self, iid):
        del self._write_invitations[iid]

    def update_invitation(self, iid, **updates):
        self._write_invitations[iid]['updated'] = utcnow_tz_aware()
        for key, value in updates.items():
            if key in ('recipient', 'inviter', 'role', 'comment'):
                self._write_invitations[iid][key] = value
            elif key == 'target':
                self._write_invitations[iid]['target_uuid'] = IUUID(value)
            else:
                raise KeyError(key)

    def iter_invitations_for_context(self, context):
        uuid = IUUID(context)
        for iid, data in self._read_invitations.items():
            if data['target_uuid'] == uuid:
                yield self.get_invitation(iid)

    def iter_invitations_for_recipient_email(self, email):
        for iid, data in self._read_invitations.items():
            if data['recipient_email'] == email:
                yield self.get_invitation(iid)

    def iter_invitations_for_inviter(self, userid):
        for iid, data in self._read_invitations.items():
            if data['inviter'] == userid:
                yield self.get_invitation(iid)

    def _generate_iid(self):
        iid = uuid.uuid4().hex
        if iid in self._read_invitations:
            return self.generate_iid()
        else:
            return iid

    def _find_user_id_for_email(self, email):
        pas_search = getMultiAdapter((api.portal.get(), getRequest()),
                                     name='pas_search')
        users = pas_search.searchUsers(email=email)
        if len(users) > 1:
            raise MultipleUsersFound("Found mulitple users for {}".format(email))
        elif len(users) == 0:
            return None

        return users[0].get('userid')

    def _has_pending_invitation(self, target, recipient_email):
        target_uuid = IUUID(target)
        for iid, data in self._read_invitations.items():
            if data['target_uuid'] != target_uuid:
                continue
            if data['status'] != STATE_PENDING:
                continue

            if data['recipient_email'] == recipient_email:
                return True

    @property
    def _write_invitations(self):
        """The invitations storage for writing.
        """
        if self.ANNOTATIONS_DATA_KEY not in self.portal_annotations:
            self.portal_annotations[self.ANNOTATIONS_DATA_KEY] = OOBTree()
        return self._read_invitations

    @property
    def _read_invitations(self):
        """The invitations storage for reading.
        """
        if self.ANNOTATIONS_DATA_KEY in self.portal_annotations:
            return self.portal_annotations[self.ANNOTATIONS_DATA_KEY]
        else:
            return {}

    def send_invitation_mail(self, iid):
        invitation = self.get_invitation(iid)
        mailer = InvitationMailer()
        mailer.send_invitation(invitation)
