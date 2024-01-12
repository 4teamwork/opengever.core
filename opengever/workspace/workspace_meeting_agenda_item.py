from Acquisition import aq_inner
from Acquisition import aq_parent
from collective import dexteritytextindexer
from opengever.base.source import WorkspacePathSourceBinder
from opengever.workspace import _
from opengever.workspace.interfaces import IWorkspaceMeetingAgendaItem
from plone.app.textfield import RichText
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Item
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.interface import implements
from zope.interface import provider


@provider(IFormFieldProvider)
class IWorkspaceMeetingAgendaItemSchema(model.Schema):

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u'label_title', default='Title'),
        required=True)

    dexteritytextindexer.searchable('text')
    text = RichText(
        title=_(u'label_text', default='Text'),
        required=False,
        default_mime_type='text/html',
        output_mime_type='text/x-html-safe')

    dexteritytextindexer.searchable('text')
    decision = RichText(
        title=_(u'label_decision', default='Decision'),
        required=False,
        default_mime_type='text/html',
        output_mime_type='text/x-html-safe')

    relatedItems = RelationList(
        title=_(u'label_related_items', default=u'Related items'),
        default=list(),
        missing_value=list(),
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

    related_todo_list = RelationChoice(
        title=_(u'label_related_todo_list', default=u'Related todo list'),
        source=WorkspacePathSourceBinder(
            portal_type=("opengever.workspace.todolist"),
        ),
        default=None,
        required=False,
    )


class WorkspaceMeetingAgendaItem(Item):
    implements(IWorkspaceMeetingAgendaItem)

    def get_containing_meeting(self):
        """Return the workspace meeting containing the agendaitem.
        """
        return aq_parent(aq_inner(self))
