from opengever.dossier.base import DossierContainer
from opengever.workspace.interfaces import IWorkspaceFolder
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope.interface import implements
from zope.interface import provider


@provider(IFormFieldProvider)
class IWorkspaceFolderSchema(model.Schema):
    """ """


class WorkspaceFolder(DossierContainer):
    implements(IWorkspaceFolder)
