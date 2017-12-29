from ftw.keywordwidget.widget import KeywordFieldWidget
from opengever.core import _
from opengever.task.task import Task, ITask
from opengever.workspace.sources import WorkspaceTaskSourceBinder
from plone.autoform import directives as form
from zope import schema


class WorkspaceTask(Task):
    """ Task for workspaces """


class IWorkspaceTask(ITask):
    """ Schema for workspace tasks """

    form.widget('responsible', KeywordFieldWidget, async=True)
    responsible = schema.List(
        title=_(u"label_responsible", default=u"Responsible"),
        description=_(u"help_responsible_multiple", default=""),
        value_type=schema.Choice(
            source=WorkspaceTaskSourceBinder()),
        required=True,
        missing_value=[],
        default=[]
        )
