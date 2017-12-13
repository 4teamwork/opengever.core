from opengever.workspace.interfaces import IWorkspace
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope.interface import implements
from zope.interface import provider
from opengever.dossier.base import DossierContainer


@provider(IFormFieldProvider)
class IWorkspaceSchema(model.Schema):
    """ """


class Workspace(DossierContainer):
    implements(IWorkspace)
