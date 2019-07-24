from collective import dexteritytextindexer
from opengever.workspace import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implements
from opengever.workspace.interfaces import IToDoList
from zope.interface import provider


@provider(IFormFieldProvider)
class IToDoListSchema(model.Schema):

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u'label_title', default='Title'),
        required=True)


class ToDoList(Container):
    """Contenttype class for TodoLists used inside workspaces.
    """

    implements(IToDoList)
