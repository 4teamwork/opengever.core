from collective import dexteritytextindexer
from ftw.keywordwidget.widget import KeywordFieldWidget
from opengever.ogds.base.sources import AllUsersSourceBinder
from opengever.workspace import _
from opengever.workspace.interfaces import IToDo
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implements
from zope.interface import provider


@provider(IFormFieldProvider)
class IToDoSchema(model.Schema):

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u'label_title', default='Title'),
        required=True)

    dexteritytextindexer.searchable('text')
    text = schema.Text(
        title=_(u'label_text', default='Text'),
        required=False)

    form.widget('responsible', KeywordFieldWidget, async=True)
    responsible = schema.Choice(
        title=_('label_responsible', default='Responsible'),
        source=AllUsersSourceBinder(),
        required=False,
    )

    deadline = schema.Date(
        title=_(u'label_deadline', default='Deadline'),
        required=False)

    completed = schema.Bool(
        title=_(u'label_completed', default='Completed'),
        default=False,
        required=False)


class ToDo(Container):
    implements(IToDo)
