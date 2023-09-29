from opengever.base.default_values import set_default_values
from opengever.dossier.utils import check_subdossier_depth_allowed
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
        return Actor.lookup(
            self.getOwner().getId()).get_label(self).encode('utf-8')

    def notifyMemberAreaCreated(self):
        """Add additional local_roles to the members folder.

        This method is called by the MembershipTool after MembersFolder
        creation.
        """
        api.user.grant_roles(username=self.getOwner().getId(), obj=self,
                             roles=PRIVATE_FOLDER_DEFAULT_ROLES)

        # MembershipTool.createMemberarea() uses yet another way for content
        # creation, that doesn't properly set default values. We therefore
        # apply them here after creation.
        set_default_values(self, self.aq_parent, {})

    def is_dossier_structure_addable(self, depth=1):
        return check_subdossier_depth_allowed(depth - 1)
