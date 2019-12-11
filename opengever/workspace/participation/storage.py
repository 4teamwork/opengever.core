from BTrees.OOBTree import OOBTree
from opengever.base.date_time import utcnow_tz_aware
from persistent.mapping import PersistentMapping
from plone.uuid.interfaces import IUUID
from zope.annotation.interfaces import IAnnotations
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import Interface
import uuid


class IInvitationStorage(Interface):
    pass


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

    def add_invitation(self, target, recipient, inviter, role):
        iid = self._generate_iid()
        self._write_invitations[iid] = PersistentMapping({
            'iid': iid,
            'target_uuid': IUUID(target),
            'recipient': recipient,
            'inviter': inviter,
            'role': role,
            'created': utcnow_tz_aware(),
            'updated': None})
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
            if key in ('recipient', 'inviter', 'role'):
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

    def iter_invitations_for_recipient(self, userid):
        for iid, data in self._read_invitations.items():
            if data['recipient'] == userid:
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
