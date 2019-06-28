from ftw.keywordwidget.widget import KeywordFieldWidget
from opengever.ogds.base.sources import AllUsersSourceBinder
from opengever.workspace import _
from opengever.workspace.interfaces import IToDo
from opengever.workspace.interfaces import IWorkspace
from plone.app.content.namechooser import NormalizingNameChooser
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.annotation import IAnnotations
from zope.component import adapter
from zope.container.interfaces import INameChooser
from zope.interface import implements
from zope.interface import provider


@provider(IFormFieldProvider)
class IToDoSchema(model.Schema):

    title = schema.TextLine(title=_(u'label_title', default='Title'), required=True)
    text = schema.Text(title=_(u'label_text', default='Text'), required=False)

    form.widget('responsible', KeywordFieldWidget, async=True)
    responsible = schema.Choice(
        title=_('label_responsible', default='Responsible'),
        source=AllUsersSourceBinder(),
        required=False,
    )
    deadline = schema.Date(title=_(u'label_deadline', default='Deadline'), required=False)
    completed = schema.Bool(
        title=_(u'label_completed', default='Completed'),
        required=False, default=False)


class ToDo(Container):
    implements(IToDo)


@provider(INameChooser)
@adapter(IWorkspace)
class ToDoNameChooser(NormalizingNameChooser):
    """ We change the behavior to auto-increment a number so that we have an
    auto-increment todo id.
    """

    def chooseName(self, name, obj):
        if IToDo.providedBy(obj):
            return self.get_next_issue_name()
        return super(ToDoNameChooser, self).chooseName(name, obj)

    def get_next_issue_name(self):
        ann_key = 'opengever.workspace.todo:last-todo-number'
        annotations = IAnnotations(self.context)
        number = annotations.get(ann_key, 0) + 1
        annotations[ann_key] = number
        return 'todo-{}'.format(str(number))
