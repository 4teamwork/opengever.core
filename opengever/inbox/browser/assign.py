from Products.CMFCore.utils import getToolByName
from five import grok
from opengever.inbox import _
from opengever.inbox.forwarding import IForwarding
from opengever.ogds.base.autocomplete_widget import AutocompleteFieldWidget
from opengever.task import _ as task_mf
from opengever.task.browser.assign import AssignTaskForm
from opengever.task.browser.assign import IAssignSchema
from plone.directives import form
from plone.z3cform import layout
from plone.z3cform.fieldsets.utils import move
from z3c.form.field import Fields
from z3c.form.interfaces import INPUT_MODE
from zope import schema


class IForwardingAssignSchema(IAssignSchema):

    form.widget(responsible=AutocompleteFieldWidget)
    responsible = schema.Choice(
        title=task_mf(u"label_responsible", default=u"Responsible"),
        description=task_mf(u"help_responsible", default=""),
        vocabulary=u'opengever.ogds.base.InboxesVocabulary',
        required=True,
        )


class AssignForwardingForm(AssignTaskForm):

    fields = Fields(IForwardingAssignSchema)
    fields['responsible'].widgetFactory[INPUT_MODE] = AutocompleteFieldWidget
    ignoreContext = True

    label = _(u'title_assign_forwarding', u'Assign Forwarding')

    def updateWidgets(self):
        super(AssignForwardingForm, self).updateWidgets()
        self.widgets['responsible_client'].mode = INPUT_MODE

    def update(self):
        move(self, 'text', after='*')
        super(AssignForwardingForm, self).update()

    def update_task(self, **kwargs):
        wf_tool = getToolByName(self.context, 'portal_workflow')
        wf_tool.doActionFor(self.context, kwargs.get('transition'))
        super(AssignForwardingForm, self).update_task(**kwargs)

class AssignForwardingView(layout.FormWrapper, grok.View):
    grok.context(IForwarding)
    grok.name('assign-forwarding')
    grok.require('zope2.View')

    form = AssignForwardingForm

    def __init__(self, *args, **kwargs):
        layout.FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)

    __call__ = layout.FormWrapper.__call__
