from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from opengever.ogds.base.autocomplete_widget import AutocompleteFieldWidget
from opengever.ogds.base.utils import get_client_id
from opengever.task import _
from opengever.task.interfaces import IWorkflowStateSyncer
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
from opengever.task.util import getTransitionVocab
from plone.directives import form
from plone.z3cform import layout
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import INPUT_MODE
from zope import schema
from zope.component import getMultiAdapter
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class IAssignSchema(form.Schema):
    """ Form schema interface for assign wizard which makes it possible to
    a task to another person.
    """
    # hidden
    transition = schema.Choice(
        title=_("label_transition", default="Transition"),
        description=_(u"help_transition", default=""),
        source=getTransitionVocab,
        required=True,
        )

    responsible_client = schema.Choice(
        title=_(u'label_resonsible_client',
                default=u'Responsible Client'),
        description=_(u'help_responsible_client',
                      default=u''),
        vocabulary='opengever.ogds.base.OrgUnitsVocabularyFactory',
        required=True)

    responsible = schema.Choice(
        title=_(u"label_responsible", default=u"Responsible"),
        description=_(u"help_responsible_single_client_setup", default=""),
        vocabulary=u'opengever.ogds.base.UsersAndInboxesVocabulary',
        required=True,
        )

    text = schema.Text(
        title=_('label_response', default="Response"),
        description=_('help_response', default=""),
        required=False,
        )


@form.default_value(field=IAssignSchema['responsible_client'])
def responsible_client_default_value(data):
    return data.context.responsible_client


class AssignTaskForm(Form):
    """Form for assigning task.
    """

    fields = Fields(IAssignSchema)
    fields['responsible'].widgetFactory[INPUT_MODE] = \
        AutocompleteFieldWidget
    ignoreContext = True

    label = _(u'title_assign_task', u'Assign task')

    def updateActions(self):
        super(AssignTaskForm, self).updateActions()
        self.actions["save"].addClass("context")

    @buttonAndHandler(_(u'button_assign', default=u'Assign'), name='save')
    def handle_assign(self, action):
        data, errors = self.extractData()
        if not errors:
            if self.context.responsible_client == data['responsible_client'] \
                    and self.context.responsible == data['responsible']:
                # no changes
                msg = _(u'error_same_responsible',
                        default=u'No changes: same responsible selected')
                IStatusMessage(self.request).addStatusMessage(
                    msg, type='error')
                return self.request.RESPONSE.redirect('.')

            self.reassing_task(**data)

        return self.request.RESPONSE.redirect('.')

    def reassing_task(self, **kwargs):
        self.add_response(**kwargs)
        self.update_task(**kwargs)
        notify(ObjectModifiedEvent(self.context))
        self.sync_remote_task(**kwargs)

    def update_task(self, **kwargs):
        self.context.responsible_client = kwargs.get('responsible_client')
        self.context.responsible = kwargs.get('responsible')

    def add_response(self, **kwargs):
        add_simple_response(
            self.context,
            text=kwargs.get('text'),
            field_changes=(
                (ITask['responsible'], kwargs.get('responsible')),
                (ITask['responsible_client'],
                 kwargs.get('responsible_client')),),
            transition=kwargs.get('transition'))

    def sync_remote_task(self, **kwargs):
        syncer = getMultiAdapter(
            (self.context, self.request), IWorkflowStateSyncer)

        syncer.change_remote_tasks_workflow_state(
            kwargs.get('transition'),
            text=kwargs.get('text'),
            responsible=kwargs.get('responsible'),
            responsible_client=kwargs.get('responsible_client'))

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect('.')

    def updateWidgets(self):
        super(AssignTaskForm, self).updateWidgets()

        # Prefill the responsible_client based on forwarding
        fwd = self.context
        self.widgets['responsible_client'].value = [fwd.responsible_client]
        self.widgets['responsible_client'].mode = HIDDEN_MODE
        self.widgets['transition'].mode = HIDDEN_MODE


class AssignTaskView(layout.FormWrapper, grok.View):
    grok.context(ITask)
    grok.name('assign-task')
    grok.require('zope2.View')

    form = AssignTaskForm

    def __init__(self, *args, **kwargs):
        layout.FormWrapper.__init__(self, *args, **kwargs)
        grok.View.__init__(self, *args, **kwargs)

    __call__ = layout.FormWrapper.__call__


class RefuseForwardingView(grok.View):
    """A view which reassign the forwarding to the inbox of the client
    which raised the forwarding, so that it can be reassigned
    afterwards to another client / person."""

    grok.context(ITask)
    grok.name('refuse-task')
    grok.require('zope2.View')

    def render(self):
        # set responsible
        self.context.responsible_client = get_client_id()
        self.context.responsible = u'inbox:%s' % (
            self.context.responsible_client)

        # create a response in the task
        add_simple_response(
            self.context,
            field_changes=(
                (ITask['responsible'], self.context.responsible),
                (ITask['responsible_client'],
                 self.context.responsible_client),),
            transition=u'forwarding-transition-refuse')

        notify(ObjectModifiedEvent(self.context))

        return self.request.RESPONSE.redirect('.')
