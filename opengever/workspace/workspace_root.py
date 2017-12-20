from interfaces import IWorkspaceRoot
from opengever.base.behaviors.translated_title import TranslatedTitleMixin
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.supermodel import model
from zope.interface import implements
from zope.interface import provider


@provider(IFormFieldProvider)
class IWorkspaceRootSchema(model.Schema):
    """ Workspace root is only here for containing other objects so it doesnt
        need any specific schema fields """


class WorkspaceRoot(Container, TranslatedTitleMixin):
    implements(IWorkspaceRoot)

    Title = TranslatedTitleMixin.Title
