from opengever.workspace.participation.storage import IInvitationStorage
from persistent import Persistent
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite
from zope.interface import implements
from zope.interface import Interface


class IInvitation(Interface):
    """A invitation
    """

    def __init__(target, userid, inviter, roles):
        """Creates a new `Invitation` on the `target` for `userid`. The
        invitation was created by `inviter` (userid). Roles are the given
        additional roles for the user (userid)
        """

    def set_target(obj):
        """Sets the target to the given `obj`. Internally we store UIDs.
        """

    def get_target():
        """Returns the currently stored target or `None`
        """


class Invitation(Persistent):
    """The `Invitation` object is used for storing who has invited who for
    which context.
    """

    implements(IInvitation)

    def __init__(self, target, userid, inviter, role):
        # get the storage
        storage = IInvitationStorage(target)
        # set the attributes
        self.userid = userid
        self.inviter = inviter
        self.set_target(target)
        self.role = role
        # generate the id, which sets it to self.iid
        storage.generate_iid_for(self)
        # register the invitation
        storage.add_invitation(self)

    def set_target(self, obj):
        self._target = IUUID(obj)

    def get_target(self):
        if '_target' not in dir(self):
            return None
        site = getSite()
        catalog = getToolByName(site, 'portal_catalog')

        result = catalog.unrestrictedSearchResults(UID=self._target)
        if len(result) != 1:
            return None
        else:
            brain, = result
            return site.unrestrictedTraverse(brain.getPath())
