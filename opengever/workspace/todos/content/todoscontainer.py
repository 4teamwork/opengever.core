from opengever.workspace import _
from opengever.workspace.interfaces import IToDo
from opengever.workspace.interfaces import IToDosContainer
from plone.app.content.namechooser import NormalizingNameChooser
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.supermodel.model import Schema
from zope.annotation import IAnnotations
from zope.component import adapter
from zope.container.interfaces import INameChooser
from zope.interface import implements
from zope.interface import provider


@provider(IFormFieldProvider)
class IToDosContainerSchema(Schema):
    pass


class ToDosContainer(Container):
    implements(IToDosContainer)

    # The container should always have the name "issues"
    # and there can only be one per workspace.
    @property
    def id(self):
        return 'todos'

    @id.setter
    def id(self, value):
        if value in (None, 'todos'):
            return
        raise ValueError('Invalid id {!r}, must be "todos".'.format(value))

    def Title(self):
        return _(u'Issues')


@provider(INameChooser)
@adapter(IToDosContainer)
class TodosContainerNameChooser(NormalizingNameChooser):
    """The name chooser for the issue container chooses the name of its
    children, which are usually issues.
    We change the behavior to auto-increment a number so that we have an
    auto-increment issue id.
    """

    def chooseName(self, name, obj):
        if IToDo.providedBy(obj):
            return self.get_next_issue_name()
        return super(TodosContainerNameChooser, self).chooseName(name, obj)

    def get_next_issue_name(self):
        ann_key = 'opengever.workspace.todo:last-todo-number'
        annotations = IAnnotations(self.context)
        number = annotations.get(ann_key, 0) + 1
        annotations[ann_key] = number
        return str(number)
