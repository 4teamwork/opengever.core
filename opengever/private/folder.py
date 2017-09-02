from opengever.ogds.base.actor import Actor
from opengever.private.interfaces import IPrivateContainer
from opengever.repository.repositoryfolder import IRepositoryFolderSchema
from plone import api
from plone.dexterity.content import Container

PRIVATE_FOLDER_DEFAULT_ROLES = [
    'Owner', 'Reader', 'Contributor', 'Editor', 'Reviewer', 'Publisher']


class IPrivateFolder(IRepositoryFolderSchema, IPrivateContainer):
    """Private folder marker and schema interface.
    """


class PrivateFolder(Container):
    """A private folder, container for all PrivateDossiers.

    Created automatically by the portal_membership tool for every user on
    the first login.
    """

    def Title(self):
        return Actor.lookup(self.id).get_label(self).encode('utf-8')

    def notifyMemberAreaCreated(self):
        """Add additional local_roles to the members folder.

        This method is called by the MembershipTool after MembersFolder
        creation.
        """
        api.user.grant_roles(username=self.id, obj=self,
                             roles=PRIVATE_FOLDER_DEFAULT_ROLES)
