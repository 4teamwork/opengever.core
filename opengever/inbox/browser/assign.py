from ftw.keywordwidget.widget import KeywordWidget
from opengever.inbox import _
from opengever.ogds.base.sources import AllUsersInboxesAndTeamsSourceBinder
from opengever.task import _ as task_mf
from opengever.task.browser.assign import AssignTaskForm
from opengever.task.browser.assign import IAssignSchema
from plone.autoform.widgets import ParameterizedWidget
from plone.z3cform import layout
from plone.z3cform.fieldsets.utils import move
from Products.CMFCore.utils import getToolByName
from z3c.form.field import Fields
from z3c.form.interfaces import INPUT_MODE
from zope import schema


class IForwardingAssignSchema(IAssignSchema):

    responsible = schema.Choice(
        title=task_mf(u"label_responsible", default=u"Responsible"),
        description=task_mf(u"help_responsible", default=""),
        source=AllUsersInboxesAndTeamsSourceBinder(include_teams=True),
        required=True,
    )


class AssignForwardingForm(AssignTaskForm):

    fields = Fields(IForwardingAssignSchema)
    fields['responsible'].widgetFactory[INPUT_MODE] = ParameterizedWidget(
        KeywordWidget,
        async=True
    )

    ignoreContext = True
    allow_prefill_from_GET_request = True  # XXX

    label = _(u'title_assign_forwarding', u'Assign Forwarding')

    def updateWidgets(self):
        super(AssignForwardingForm, self).updateWidgets()

    def update(self):
        move(self, 'text', after='*')
        super(AssignForwardingForm, self).update()

    def update_task(self, **kwargs):
        wf_tool = getToolByName(self.context, 'portal_workflow')
        wf_tool.doActionFor(self.context, kwargs.get('transition'))
        super(AssignForwardingForm, self).update_task(**kwargs)


class AssignForwardingView(layout.FormWrapper):

    form = AssignForwardingForm
