from datetime import datetime
from hashlib import md5
from persistent.dict import PersistentDict
from persistent.list import PersistentList
from plone import api
from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAnnotations
from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface


class IInvitationStorage(Interface):
    """Marker interface for invitation storage.
    """


STORAGE_CACHE_KEY = '_invitations_list'


class InvitationStorage(object):
    """The invitation stores and manages the invitation. All modification in
    the list of invitations (appending new invitations, deleting existing
    invitations, etc.) should be done with through the invitation storage.
    The invitation storage is adapter adapting any context. The storage stores
    its data into annotations on the plone site root.
    """

    implements(IInvitationStorage)
    adapts(Interface)

    ANNOTATIONS_DATA_KEY = 'opengever.workspace : invitations'

    def __init__(self, context):
        """Adapts any context within a plone site
        """
        self.context = context
        portal_url = getToolByName(self.context, 'portal_url')
        self.portal = portal_url.getPortalObject()

    @property
    def portal_annotations(self):
        """The annotations of the plone site root
        """
        return IAnnotations(self.portal)

    @property
    def invitations(self):
        """A persistent dictionary of all invitations. The key is the userid
        of the invited user, the values are `PersistentList`s of
        `Invitations` of this user.
        """
        if STORAGE_CACHE_KEY not in dir(self):
            if self.ANNOTATIONS_DATA_KEY not in self.portal_annotations:
                return {}
            else:
                # didnt cache it yet, get it from the annotations (and cache it)
                setattr(self, STORAGE_CACHE_KEY,
                        self.portal_annotations[self.ANNOTATIONS_DATA_KEY])

        return getattr(self, STORAGE_CACHE_KEY, {})

    def initialize_storage(self):
        if self.ANNOTATIONS_DATA_KEY not in self.portal_annotations:
            # dictionary does not exist in the annotations, create it
            self.portal_annotations[self.ANNOTATIONS_DATA_KEY] = PersistentDict()

    def get_used_iids(self):
        """Returns a dict of all currently existing invitations with their id
        as key. This method is complex, do not use it often :)
        """

        if self.invitations is None:
            return {}

        data = {}
        for userid, users_invitiations in self.invitations.items():
            for invitation in users_invitiations:
                data[invitation.iid] = invitation
        return data

    def generate_iid_for(self, invitation):
        """Generates a invitation id for the invitation and sets it (and
        returns it eventually).
        """
        used_iids = self.get_used_iids()
        # create a string as unique as possible, which will be hashed later
        # for that the info of the string are not decodable by the user
        base = '-'.join((
            str(datetime.now().isoformat()),
            invitation.userid,
            invitation.inviter))
        counter = 1
        iid = None
        while not iid or iid in used_iids:
            iid = md5(base + str(counter)).hexdigest().strip()
            counter += 1
        # set the iid on the invitation
        invitation.iid = iid
        return iid

    def get_invitation_by_iid(self, iid, default=None):
        """Returns the invitation with the `iid` or `default` if there is none.
        """
        for users_invitiations in self.invitations.values():
            for invitation in users_invitiations:
                for invitation in users_invitiations:
                    if invitation.iid == iid:
                        return invitation
        return default

    def get_invitations_by_userid(self, userid=None, default=[]):
        """Returns a list of invitations for a specific userid. If
        `userid` is `None` the userid of the currently authenticated user.
        If there are no results, `default` is returned.
        """
        if userid is None:
            userid = api.user.get_current().getId()
        if userid in self.invitations:
            return self.invitations.get(userid)
        else:
            return default

    def get_invitations_invited_by(self, userid=None, default=[]):
        """Returns a list of invitations which are created by a specific user
        for any userid. If `userid` is `None` the userid of the
        authenticated member is taken. If there are no results, `default`
        is returned.
        """
        # guess the `userid` if its `None`
        if userid is None:
            userid = api.user.get_current().getId()

        # find all inivitations where the inviter is `userid`
        list_ = []
        for users_invitiations in self.invitations.values():
            for inv in users_invitiations:
                if inv.inviter == userid:
                    list_.append(inv)
        return list_ or default

    def get_invitations_for_context(self, context, default=[]):
        """Returns all invitations for a context. This method may be slow.
        """
        list_ = []
        for users_invitiations in self.invitations.values():
            for inv in users_invitiations:
                if inv.get_target() == context:
                    list_.append(inv)
        return list_ or default

    def add_invitation(self, invitation):
        """Adds a invitation object to the storage.
        """

        # Init storage if not yet there:
        self.initialize_storage()

        # the key of the invitations dict is `invitaiton.userid`, the value
        # is a `PersistentDict`
        if invitation.userid not in self.invitations:
            self.invitations[invitation.userid] = PersistentList()
        # check if its already added
        if invitation in self.invitations[invitation.userid]:
            return False
        else:
            self.invitations[invitation.userid].append(invitation)

    def remove_invitation(self, invitation):
        """Removes the `invitation` from the storage and destroys it
        """
        if invitation.userid in self.invitations and \
                invitation in self.invitations[invitation.userid]:
            # if the invitation is stored under invitation.userid remove
            # it from there...
            self.invitations[invitation.userid].remove(invitation)
            if len(self.invitations[invitation.userid]) == 0:
                del self.invitations[invitation.userid]
            return True
        return False
