from Acquisition import aq_inner
from Acquisition import aq_parent
from collective import dexteritytextindexer
from ftw.keywordwidget.widget import KeywordFieldWidget
from opengever.base.response import IResponseSupported
from opengever.ogds.base.sources import ActualWorkspaceMembersSourceBinder
from opengever.workspace import _
from opengever.workspace.interfaces import IToDo
from opengever.workspace.interfaces import IWorkspace
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.supermodel import model
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
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
        source=ActualWorkspaceMembersSourceBinder(),
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
    implements(IToDo, IResponseSupported)

    def get_containing_workspace(self):
        """Return the workspace containing the todo.
        Every ToDo should be contained in a workspace.
        """
        obj = self

        while not IPloneSiteRoot.providedBy(obj):
            parent = aq_parent(aq_inner(obj))
            if IWorkspace.providedBy(parent):
                return parent
            obj = parent
        return None
