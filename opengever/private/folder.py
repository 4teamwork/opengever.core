from opengever.ogds.base.actor import Actor
from opengever.repository.repositoryfolder import IRepositoryFolderSchema
from plone.dexterity.content import Container


class IPrivateFolder(IRepositoryFolderSchema, IPrivateContainer):
    """Private folder marker and schema interface.
    """


class PrivateFolder(Container):
    """A private folder, container for all PrivateDossiers.

    Created automatically by the portal_membership tool for every user on
    the first login.
    """

    def Title(self):
        return Actor.lookup(self.id).get_label(self)
