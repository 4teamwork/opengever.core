from ftw.keywordwidget.widget import KeywordWidget
from opengever.ogds.base.actor import ActorLookup
from opengever.ogds.base.sources import AllUsersInboxesAndTeamsSourceBinder
from opengever.ogds.base.utils import get_current_org_unit
from opengever.ogds.base.utils import ogds_service
from opengever.task import _
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
from opengever.task.util import getTransitionVocab
from opengever.task.util import update_reponsible_field_data
from plone import api
from plone.autoform.widgets import ParameterizedWidget
from plone.supermodel.model import Schema
from plone.z3cform.layout import FormWrapper
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import validator
from z3c.form.button import buttonAndHandler
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.interfaces import HIDDEN_MODE
from z3c.form.interfaces import INPUT_MODE
from zope import schema
from zope.event import notify
from zope.interface import Invalid
from zope.lifecycleevent import ObjectModifiedEvent


class IAssignSchema(Schema):
    """ Form schema interface for assign wizard which makes it possible to
    a task to another person.
    """
    # hidden
    transition = schema.Choice(
        title=_("label_transition", default="Transition"),
        source=getTransitionVocab,
        required=True,
        )

    responsible = schema.Choice(
        title=_(u"label_responsible", default=u"Responsible"),
        description=_(u"help_responsible", default=""),
        source=AllUsersInboxesAndTeamsSourceBinder(
            only_current_inbox=False,
            only_current_orgunit=False,
            include_teams=True),
        required=True,
        )

    text = schema.Text(
        title=_('label_response', default="Response"),
        required=False,
        )


class InProgressStateLimitiationsValidator(validator.SimpleFieldValidator):
    """Tasks not in the open state are limited:

    - Teams are only allowed if the task/forwarding is in open state.
    - Admin unit changes are only allowed in open state.
    """

    def validate(self, value):
        if value and not self.context.is_open():
            if ActorLookup(value).is_team():
                raise Invalid(
                    _(u'error_no_team_responsible_in_progress_state',
                      default=u'Team responsibles are only allowed if the task or '
                      u'forwarding is open.'))

            responsible_client, responsible = value.split(':')
            new_admin_unit = ogds_service().fetch_org_unit(
                responsible_client).admin_unit
            if self.context.get_responsible_admin_unit().id() != new_admin_unit.id():
                raise Invalid(
                    _(u'error_no_admin_unit_change_in_progress_state',
                      default=u'Admin unit changes are not allowed if the task or '
                      u'forwarding is already accepted.'))


validator.WidgetValidatorDiscriminators(
    InProgressStateLimitiationsValidator,
    field=IAssignSchema['responsible'],
)


class AssignTaskForm(Form):
    """Form for assigning task.
    """

    fields = Fields(IAssignSchema)
    fields['responsible'].widgetFactory[INPUT_MODE] = ParameterizedWidget(
        KeywordWidget,
        async=True
    )

    ignoreContext = True
    allow_prefill_from_GET_request = True  # XXX

    label = _(u'title_assign_task', u'Assign task')

    def updateActions(self):
        super(AssignTaskForm, self).updateActions()
        self.actions["save"].addClass("context")

    @buttonAndHandler(_(u'button_assign', default=u'Assign'), name='save')
    def handle_assign(self, action):
        data, errors = self.extractData()

        if not errors:
            update_reponsible_field_data(data)
            if self.context.responsible_client == data['responsible_client'] \
                    and self.context.responsible == data['responsible']:
                # no changes
                msg = _(u'error_same_responsible',
                        default=u'No changes: same responsible selected')
                IStatusMessage(self.request).addStatusMessage(
                    msg, type='error')
                return self.request.RESPONSE.redirect(
                    self.context.absolute_url())

            self.reassign_task(**data)

            return self.redirect()

    def redirect(self):
        """Redirects to task if the current user still has View permission,
        otherwise it redirects to portal.
        """
        if api.user.has_permission('View', obj=self.context):
            msg = _(u'msg_successfully_reassigned',
                    default=u'Task successfully reassigned.')
            api.portal.show_message(msg, request=self.request, type='info')
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        msg = _(u'msg_successfully_reassigned_no_longer_permission',
                default=u'Task successfully reassigned. You are no '
                'longer permitted to access the task.')
        api.portal.show_message(msg, request=self.request, type='info')
        return self.request.RESPONSE.redirect(api.portal.get().absolute_url())

    def reassign_task(self, **kwargs):
        wftool = api.portal.get_tool('portal_workflow')
        wftool.doActionFor(self.context, kwargs.pop('transition'),
                           comment=kwargs.get('text'), transition_params=kwargs)

    @buttonAndHandler(_(u'button_cancel', default=u'Cancel'))
    def handle_cancel(self, action):
        return self.request.RESPONSE.redirect('.')

    def updateWidgets(self):
        super(AssignTaskForm, self).updateWidgets()
        self.widgets['transition'].mode = HIDDEN_MODE


class AssignTaskView(FormWrapper):

    form = AssignTaskForm


class RefuseForwardingView(BrowserView):
    """A view which reassign the forwarding to the inbox of the client
    which raised the forwarding, so that it can be reassigned
    afterwards to another client / person."""

    def __call__(self):
        # set responsible
        org_unit = get_current_org_unit()
        self.context.responsible_client = org_unit.id()
        self.context.responsible = org_unit.inbox().id()

        # create a response in the task
        add_simple_response(
            self.context,
            field_changes=(
                (ITask['responsible'], self.context.responsible),
                (ITask['responsible_client'],
                 self.context.responsible_client),),
            transition=u'forwarding-transition-refuse',
            supress_events=True)

        notify(ObjectModifiedEvent(self.context))

        return self.request.RESPONSE.redirect('.')
