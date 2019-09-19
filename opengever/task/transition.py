from Acquisition import aq_parent
from opengever.activity import notification_center
from opengever.activity.roles import TASK_RESPONSIBLE_ROLE
from opengever.base.source import DossierPathSourceBinder
from opengever.base.transition import ITransitionExtender
from opengever.base.transition import TransitionExtender
from opengever.ogds.base.sources import AllUsersInboxesAndTeamsSourceBinder
from opengever.task import _
from opengever.task.activities import TaskAddedActivity
from opengever.task.activities import TaskReassignActivity
from opengever.task.browser.assign import validate_no_admin_unit_change
from opengever.task.browser.assign import validate_no_teams
from opengever.task.browser.delegate.metadata import IUpdateMetadata
from opengever.task.browser.delegate.recipients import ISelectRecipientsSchema
from opengever.task.browser.delegate.utils import create_subtasks
from opengever.task.browser.modify_deadline import validate_deadline_changed
from opengever.task.interfaces import IDeadlineModifier
from opengever.task.localroles import LocalRolesSetter
from opengever.task.reminder.reminder import TaskReminder
from opengever.task.response_syncer import sync_task_response
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
from plone import api
from plone.supermodel.model import Schema
from z3c.form import validator
from z3c.relationfield.relation import RelationValue
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.component import adapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.event import notify
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectModifiedEvent
from zope.publisher.interfaces.browser import IBrowserRequest


class IResponse(Schema):

    text = schema.Text(
        title=_('label_response', default="Response"),
        required=False,
        )

    relatedItems = RelationList(
        title=_(u'label_related_items', default=u'Related Items'),
        default=[],
        missing_value=[],
        value_type=RelationChoice(
            title=u"Related",
            source=DossierPathSourceBinder(
                portal_type=("opengever.document.document", "ftw.mail.mail"),
                navigation_tree_query={
                    'object_provides': [
                        'opengever.dossier.behaviors.dossier.IDossierMarker',
                        'opengever.document.document.IDocumentSchema',
                        'opengever.task.task.ITask',
                        'ftw.mail.mail.IMail',
                        'opengever.meeting.proposal.IProposal',
                    ],
                    },
                ),
            ),
        required=False,
    )


class INewDeadline(Schema):

    new_deadline = schema.Date(
        title=_(u"label_new_deadline", default=u"New Deadline"),
        required=True)


class INewResponsibleSchema(Schema):

    responsible = schema.Choice(
        title=_(u"label_responsible", default=u"Responsible"),
        description=_(u"help_responsible", default=""),
        source=AllUsersInboxesAndTeamsSourceBinder(
            only_current_inbox=True,
            only_current_orgunit=True,
            include_teams=True),
        required=True)

    responsible_client = schema.Choice(
        title=_(u'label_resonsible_client', default=u'Responsible Client'),
        description=_(u'help_responsible_client', default=u''),
        vocabulary='opengever.ogds.base.OrgUnitsVocabularyFactory',
        required=True)


class NoTeamsInProgressStateValidator(validator.SimpleFieldValidator):
    """Tasks not in the open state are limited:
    - Teams are only allowed if the task/forwarding is in open state.
    """

    def validate(self, value):
        if value and not self.context.is_open():
            validate_no_teams(self.context, value)


validator.WidgetValidatorDiscriminators(
    NoTeamsInProgressStateValidator,
    field=INewResponsibleSchema['responsible'],
)


class NoAdminUnitChangeInProgressStateValidator(validator.SimpleFieldValidator):
    """Admin unit changes are only allowed in open state.
    """

    def validate(self, value):
        if value and not self.context.is_open():
            validate_no_admin_unit_change(self.context, value)


validator.WidgetValidatorDiscriminators(
    NoAdminUnitChangeInProgressStateValidator,
    field=INewResponsibleSchema['responsible_client'],
)


@implementer(ITransitionExtender)
@adapter(ITask, IBrowserRequest)
class DefaultTransitionExtender(TransitionExtender):

    schemas = [IResponse, ]

    def after_transition_hook(self, transition, disable_sync, transition_params):
        response = add_simple_response(self.context, transition=transition,
                                       text=transition_params.get('text'))

        self.save_related_items(response, transition_params.get('relatedItems'))
        self.sync_change(transition, transition_params.get('text'), disable_sync)

    def save_related_items(self, response, related_items):
        if not related_items:
            return

        intids = getUtility(IIntIds)
        current_ids = [item.to_id for item in ITask(self.context).relatedItems]
        for item in related_items:
            to_id = intids.getId(item)
            item._v__is_relation = True
            if to_id not in current_ids:
                ITask(self.context).relatedItems.append(RelationValue(to_id))
                response.add_change(
                    'relatedItems',
                    _(u'label_related_items', default=u"Related Items"),
                    '', item.title)

    def sync_change(self, transition, text, disable_sync):
        if not disable_sync:
            sync_task_response(self.context, getRequest(), 'workflow',
                               transition, text)


@implementer(ITransitionExtender)
@adapter(ITask, IBrowserRequest)
class AcceptTransitionExtender(DefaultTransitionExtender):

    schemas = [IResponse, ]

    def after_transition_hook(self, transition, disable_sync, transition_params):
        response = add_simple_response(
            self.context, transition=transition, text=transition_params.get('text'))

        if self.context.is_team_task:
            self.reassign_team_task(response)

        self.save_related_items(response, transition_params.get('relatedItems'))
        self.sync_change(transition, transition_params.get('text'), disable_sync)

    def reassign_team_task(self, response):
        old_responsible = ITask(self.context).responsible
        ITask(self.context).responsible = api.user.get_current().getId()
        response.add_change(
            'responsible',
            _(u"label_responsible", default=u"Responsible"),
            old_responsible, ITask(self.context).responsible)
        self.context.sync()


@implementer(ITransitionExtender)
@adapter(ITask, IBrowserRequest)
class ModifyDeadlineTransitionExtender(TransitionExtender):

    schemas = [INewDeadline, ]

    def after_transition_hook(self, transition, disable_sync, transition_params):
        IDeadlineModifier(self.context).modify_deadline(
            transition_params['new_deadline'], transition_params.get('text'),
            transition)


class DeadlineChangedValidator(validator.SimpleFieldValidator):
    """Deadline have to be changed.
    """

    def validate(self, value):
        validate_deadline_changed(self.context, value)


validator.WidgetValidatorDiscriminators(
    DeadlineChangedValidator,
    field=INewDeadline['new_deadline'],
)


@implementer(ITransitionExtender)
@adapter(ITask, IBrowserRequest)
class ResolveTransitionExtender(DefaultTransitionExtender):

    schemas = [IResponse, ]

    def after_transition_hook(self, transition, disable_sync, transition_params):
        response = add_simple_response(
            self.context, transition=transition,
            text=transition_params.get('text'))

        self.save_related_items(response, transition_params.get('relatedItems'))
        self.sync_change(transition, transition_params.get('text'), disable_sync)


@implementer(ITransitionExtender)
@adapter(ITask, IBrowserRequest)
class CloseTransitionExtender(DefaultTransitionExtender):

    schemas = [IResponse, ]

    def after_transition_hook(self, transition, disable_sync, transition_params):
        response = add_simple_response(self.context, transition=transition,
                                       text=transition_params.get('text'))

        self.save_related_items(response, transition_params.get('relatedItems'))
        self.sync_change(transition, transition_params.get('text'), disable_sync)


@implementer(ITransitionExtender)
@adapter(ITask, IBrowserRequest)
class ReassignTransitionExtender(DefaultTransitionExtender):

    schemas = [IResponse, INewResponsibleSchema]

    def after_transition_hook(self, transition, disable_sync, transition_params):
        # Revoke local roles for current responsible, except if
        # revoke_permissions is set to False.
        # the roles for the new responsible will be assigned afterwards
        # in set_roles_after_modifying on the ObjectModifiedEvent.
        if self.context.revoke_permissions:
            LocalRolesSetter(self.context).revoke_roles()

        former_responsible = ITask['responsible']
        former_responsible_client = ITask['responsible_client']

        TaskReminder().clear_reminder(self.context, self.context.responsible)

        changes = (
            (former_responsible, transition_params.get('responsible')),
            (former_responsible_client, transition_params.get('responsible_client')))
        response = add_simple_response(
            self.context, transition=transition, text=transition_params.get('text'),
            field_changes=changes, supress_events=True)

        self.save_related_items(response, transition_params.get('relatedItems'))
        self.change_responsible(transition_params)
        notify(ObjectModifiedEvent(self.context))
        self.record_activity(response)

        if not disable_sync:
            sync_task_response(
                self.context, getRequest(), 'workflow',
                transition, transition_params.get('text'),
                responsible=transition_params.get('responsible'),
                responsible_client=transition_params.get('responsible_client'))

    def change_responsible(self, transition_params):
        self.context.responsible_client = transition_params.get('responsible_client')
        self.context.responsible = transition_params.get('responsible')

    def record_activity(self, response):
        TaskReassignActivity(self.context, self.context.REQUEST, response).record()


@implementer(ITransitionExtender)
@adapter(ITask, IBrowserRequest)
class RejectTransitionExtender(DefaultTransitionExtender):
    """Default task transition handling expect the responsible is switched
    to task's issuer.
    """

    schemas = [IResponse, ]

    def after_transition_hook(self, transition, disable_sync, transition_params):
        self.update_watchers()

        response = add_simple_response(
            self.context, transition=transition, text=transition_params.get('text'))

        response.add_change(
            'responsible',
            _(u"label_responsible", default=u"Responsible"),
            ITask(self.context).responsible, ITask(self.context).issuer)

        self.save_related_items(response, transition_params.get('relatedItems'))
        self.switch_responsible()

    def update_watchers(self):
        center = notification_center()
        center.remove_watcher_from_resource(
            self.context.oguid, self.context.responsible, TASK_RESPONSIBLE_ROLE)
        center.add_watcher_to_resource(
            self.context.oguid, self.context.issuer, TASK_RESPONSIBLE_ROLE)

    def switch_responsible(self):
        self.context.responsible = ITask(self.context).issuer


@implementer(ITransitionExtender)
@adapter(ITask, IBrowserRequest)
class DelegateTransitionExtender(DefaultTransitionExtender):

    schemas = [IUpdateMetadata, ISelectRecipientsSchema]

    def after_transition_hook(self, transition, disable_sync, transition_params):
        create_subtasks(self.context,
                        transition_params.pop('responsibles'),
                        transition_params.get('documents', []),
                        transition_params)


@implementer(ITransitionExtender)
@adapter(ITask, IBrowserRequest)
class OpenPlannedTransitionExtender(DefaultTransitionExtender):
    """Default transition extender but supress default activity and
    record an TaskAdded activity instead."""

    def after_transition_hook(self, transition, disable_sync, transition_params):
        response = add_simple_response(self.context, transition=transition,
                                       text=transition_params.get('text'),
            supress_activity=True)

        TaskAddedActivity(
            self.context, getRequest(), aq_parent(self.context)).record()

        self.save_related_items(response, transition_params.get('relatedItems'))
        self.sync_change(transition, transition_params.get('text'), disable_sync)
