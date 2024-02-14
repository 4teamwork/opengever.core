from Acquisition import aq_inner
from Acquisition import aq_parent
from collective import dexteritytextindexer
from ftw.keywordwidget.widget import KeywordFieldWidget
from opengever.base.response import IResponseSupported
from opengever.base.source import WorkspacePathSourceBinder
from opengever.ogds.base.sources import WorkspaceContentMemberUsersSourceBinder
from opengever.workspace import _
from opengever.workspace.interfaces import IToDo
from opengever.workspace.interfaces import IWorkspace
from plone import api
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.supermodel import model
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.interface import implements
from zope.interface import provider


COMPLETED_TODO_STATE = 'opengever_workspace_todo--STATUS--completed'

ACTIVE_TODO_STATE = 'opengever_workspace_todo--STATUS--active'

COMPLETE_TODO_TRANSITION = 'opengever_workspace_todo--TRANSITION--complete--active_completed'

OPEN_TODO_TRANSITION = 'opengever_workspace_todo--TRANSITION--open--completed_active'


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
        source=WorkspaceContentMemberUsersSourceBinder(),
        required=False,
    )

    deadline = schema.Date(
        title=_(u'label_deadline', default='Deadline'),
        required=False)

    relatedItems = RelationList(
        title=_(u'label_related_items', default=u'Related items'),
        default=[],
        missing_value=[],
        value_type=RelationChoice(
            title=u"Related",
            source=WorkspacePathSourceBinder(
                portal_type=("opengever.document.document", "ftw.mail.mail"),
                navigation_tree_query={
                    'review_state': {'not': 'document-state-shadow'},
                },
            ),
        ),
        required=False,
    )

    dexteritytextindexer.searchable('external_reference')
    external_reference = schema.TextLine(
        title=_(u'label_external_reference', default='External Reference'),
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

    @property
    def is_completed(self):
        return api.content.get_state(self) == COMPLETED_TODO_STATE

    def toggle(self):
        transition = OPEN_TODO_TRANSITION if self.is_completed else COMPLETE_TODO_TRANSITION
        api.content.transition(obj=self, transition=transition)
