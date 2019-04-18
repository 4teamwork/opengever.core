from opengever.workspace.interfaces import IWorkspace
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope.interface import implements
from zope.interface import provider
from plone.dexterity.content import Container


@provider(IFormFieldProvider)
class IWorkspaceSchema(model.Schema):
    """ """


class Workspace(Container):
    implements(IWorkspace)
