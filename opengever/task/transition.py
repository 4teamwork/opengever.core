from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.activity import notification_center
from opengever.activity.roles import TASK_RESPONSIBLE_ROLE
from opengever.base.source import DossierPathSourceBinder
from opengever.base.transition import ITransitionExtender
from opengever.base.transition import TransitionExtender
from opengever.base.utils import unrestrictedUuidToObject
from opengever.document.approvals import IApprovalList
from opengever.document.versioner import Versioner
from opengever.ogds.base.sources import AllUsersAndGroupsSourceBinder
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
from opengever.task.response_syncer import sync_task_response
from opengever.task.sources import DocumentsFromTaskSourceBinder
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
from plone import api
from plone.supermodel.model import Schema
from z3c.form import validator
from z3c.relationfield.relation import RelationValue
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zExceptions import BadRequest
from zope import schema
from zope.component import adapter
from zope.component import getUtility
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


class INewInformedPrincipals(Schema):

    informed_principals = schema.List(
        title=_(u"label_informed_principals", default=u"Info at"),
        description=_(u"help_informed_principals", default=u""),
        value_type=schema.Choice(
            source=AllUsersAndGroupsSourceBinder(),
        ),
        required=False,
        missing_value=[],
        default=[]
    )


class INewResponsibleSchema(Schema):

    responsible = schema.Choice(
        title=_(u"label_responsible", default=u"Responsible"),
        description=_(u"help_responsible", default=""),
        source=AllUsersInboxesAndTeamsSourceBinder(
            only_current_inbox=False,
            only_current_orgunit=True,
            include_teams=True),
        required=True)

    responsible_client = schema.Choice(
        title=_(u'label_resonsible_client', default=u'Responsible Client'),
        description=_(u'help_responsible_client', default=u''),
        vocabulary='opengever.ogds.base.OrgUnitsVocabularyFactory',
        required=True)


class IApprovedDocuments(Schema):

    approved_documents = schema.List(
        title=_(u"label_approved_documents", default=u"Approved documents"),
        description=_(u"help_approved_documents", default=u""),
        value_type=schema.Choice(
            source=DocumentsFromTaskSourceBinder(),
        ),
        required=False,
        missing_value=[],
        default=[]
    )


class IPassDocumentsToNextTask(Schema):

    pass_documents_to_next_task = schema.Bool(
        title=u'Pass documents to the next task.',
        description=u'Whether all document relations and documents of the '
                    u'previous task should be passed the next task',
        default=False,
        required=False)


class NoTeamsInProgressStateValidator(validator.SimpleFieldValidator):
    """Tasks not in the open state are limited:
    - Teams are only allowed if the task/forwarding is in open state.
    """

    def validate(self, value):
        if value and not self.context.is_open():
            validate_no_teams(self.context, value)


# this validator is relevant for API requests and used in `TransitionExtender`
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


# this validator is relevant for API requests and used in `TransitionExtender`
validator.WidgetValidatorDiscriminators(
    NoAdminUnitChangeInProgressStateValidator,
    field=INewResponsibleSchema['responsible_client'],
)


@implementer(ITransitionExtender)
@adapter(ITask, IBrowserRequest)
class DefaultTransitionExtender(TransitionExtender):

    schemas = [IResponse, IPassDocumentsToNextTask]

    def after_transition_hook(self, transition, disable_sync, transition_params):
        response = add_simple_response(self.context, transition=transition,
                                       text=transition_params.get('text'))

        self.save_related_items(response, transition_params.get('relatedItems'))
        self.pass_documents_to_next_task(transition, transition_params)
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
                    '', item.title,
                    _(u'label_related_items', default=u"Related Items"))

    def sync_change(self, transition, text, disable_sync, **kwargs):
        if not disable_sync:
            sync_task_response(self.context, getRequest(), 'workflow',
                               transition, text, **kwargs)

    def pass_documents_to_next_task(self, transition, transition_params):
        if not (
                getattr(self.context, '_v_transition_opened_next_task', False)
                and transition_params.get('pass_documents_to_next_task')):
            return

        next_task = self.context.get_sql_object().get_next_task().oguid.resolve_object()

        intids = getUtility(IIntIds)
        current_document_ids = [intids.getId(document) for document
                                in self.context.task_documents()]

        # Pass documents to all (sub)tasks that get started. So at least to
        # the next task, but also to any nested subtasks that will be started
        # if the next task happens to be a task template.
        for task in [next_task] + list(next_task._get_subtasks_to_start(next_task)):
            existing_related_items = [item.to_id for item in ITask(task).relatedItems]
            ITask(task).relatedItems = [
                RelationValue(document_int_id) for document_int_id
                in set(current_document_ids + existing_related_items)]

        return transition_params['pass_documents_to_next_task']


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
        current_user_id = api.user.get_current().getId()

        center = notification_center()
        center.add_task_responsible(self.context, current_user_id)
        center.remove_task_responsible(self.context, old_responsible)
        ITask(self.context).responsible = current_user_id
        self.context.add_former_responsible(old_responsible)
        response.add_change(
            'responsible',
            old_responsible, ITask(self.context).responsible,
            _(u"label_responsible", default=u"Responsible"))
        notify(ObjectModifiedEvent(self.context))


@implementer(ITransitionExtender)
@adapter(ITask, IBrowserRequest)
class ModifyDeadlineTransitionExtender(TransitionExtender):

    schemas = [IResponse, INewDeadline, ]

    def after_transition_hook(self, transition, disable_sync, transition_params):
        IDeadlineModifier(self.context).modify_deadline(
            transition_params['new_deadline'], transition_params.get('text'),
            transition)


class DeadlineChangedValidator(validator.SimpleFieldValidator):
    """Deadline have to be changed.
    """

    def validate(self, value):
        validate_deadline_changed(self.context, value)


# this validator is relevant for API requests and used in `TransitionExtender`
validator.WidgetValidatorDiscriminators(
    DeadlineChangedValidator,
    field=INewDeadline['new_deadline'],
)


@implementer(ITransitionExtender)
@adapter(ITask, IBrowserRequest)
class ResolveTransitionExtender(DefaultTransitionExtender):

    schemas = [IResponse, IApprovedDocuments, IPassDocumentsToNextTask]

    def after_transition_hook(self, transition, disable_sync, transition_params):
        approved_documents = self.maybe_approve_documents(transition_params)
        response = add_simple_response(
            self.context, transition=transition,
            text=transition_params.get('text'),
            approved_documents=approved_documents,
        )

        self.save_related_items(response, transition_params.get('relatedItems'))
        pass_documents = self.pass_documents_to_next_task(
            transition, transition_params)
        self.sync_change(transition,
                         transition_params.get('text'),
                         disable_sync,
                         pass_documents_to_next_task=pass_documents)

    def maybe_approve_documents(self, transition_params):
        approved_documents = transition_params.get('approved_documents', [])
        approved_documents = map(unrestrictedUuidToObject, approved_documents)

        if approved_documents:
            if not self.context.is_approval_task():
                raise BadRequest(
                    "Param 'approved_documents' is only supported for tasks "
                    "of task_type 'approval'.")

            for doc in approved_documents:
                approvals = IApprovalList(doc)
                versioner = Versioner(doc)
                current_version_id = versioner.get_current_version_id(
                    missing_as_zero=True)
                approvals.add(current_version_id, self.context)

        return approved_documents


@implementer(ITransitionExtender)
@adapter(ITask, IBrowserRequest)
class CloseTransitionExtender(DefaultTransitionExtender):

    schemas = [IResponse, IPassDocumentsToNextTask]

    def after_transition_hook(self, transition, disable_sync, transition_params):
        response = add_simple_response(self.context, transition=transition,
                                       text=transition_params.get('text'))

        self.save_related_items(response, transition_params.get('relatedItems'))
        pass_documents = self.pass_documents_to_next_task(transition, transition_params)
        parent = aq_parent(aq_inner(self.context))
        if ITask.providedBy(parent):
            add_simple_response(parent, transition='transition-close-subtask',
                                subtask=self.context)
        self.sync_change(transition,
                         transition_params.get('text'),
                         disable_sync,
                         pass_documents_to_next_task=pass_documents)


@implementer(ITransitionExtender)
@adapter(ITask, IBrowserRequest)
class CancelTransitionExtender(DefaultTransitionExtender):

    def after_transition_hook(self, transition, disable_sync, transition_params):
        super(CancelTransitionExtender, self).after_transition_hook(
            transition, disable_sync, transition_params)
        parent = aq_parent(aq_inner(self.context))
        if ITask.providedBy(parent):
            add_simple_response(parent, transition='transition-cancel-subtask',
                                subtask=self.context)


@implementer(ITransitionExtender)
@adapter(ITask, IBrowserRequest)
class ReassignTransitionExtender(DefaultTransitionExtender):

    schemas = [IResponse, INewResponsibleSchema]

    def after_transition_hook(self, transition, disable_sync, transition_params):
        self.context.clear_reminder(self.context.responsible)

        responsible_client = transition_params.get('responsible_client')
        responsible = transition_params.get('responsible')

        changes = [(ITask['responsible'], responsible)]
        if ITask(self.context).responsible_client != responsible_client:
            changes.append((ITask['responsible_client'], responsible_client))
        response = add_simple_response(
            self.context, transition=transition,
            text=transition_params.get('text'), field_changes=changes,
            supress_events=True)

        self.save_related_items(response, transition_params.get('relatedItems'))
        self.change_responsible(transition_params)
        notify(ObjectModifiedEvent(self.context))
        self.record_activity(response)

        if not disable_sync:
            sync_task_response(
                self.context, getRequest(), 'workflow',
                transition, transition_params.get('text'),
                responsible=responsible, responsible_client=responsible_client)

    def change_responsible(self, transition_params):
        self.context.add_former_responsible(self.context.responsible)
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
            ITask(self.context).responsible, ITask(self.context).issuer,
            _(u"label_responsible", default=u"Responsible"))

        self.save_related_items(response, transition_params.get('relatedItems'))
        self.switch_responsible()
        notify(ObjectModifiedEvent(self.context))

    def update_watchers(self):
        center = notification_center()
        center.remove_watcher_from_resource(
            self.context.oguid, self.context.responsible, TASK_RESPONSIBLE_ROLE)
        center.add_watcher_to_resource(
            self.context.oguid, self.context.issuer, TASK_RESPONSIBLE_ROLE)

    def switch_responsible(self):
        self.context.add_former_responsible(self.context.responsible)
        self.context.responsible = ITask(self.context).issuer


@implementer(ITransitionExtender)
@adapter(ITask, IBrowserRequest)
class DelegateTransitionExtender(DefaultTransitionExtender):

    schemas = [IUpdateMetadata, ISelectRecipientsSchema, INewInformedPrincipals]

    def after_transition_hook(self, transition, disable_sync, transition_params):
        create_subtasks(self.context,
                        transition_params.pop('responsibles'),
                        transition_params.pop('documents', []),
                        transition_params)

    def _deserialize_schema(self, schema, transition_params, collect_errors=False):
        if "text" in transition_params and transition_params["text"] is None:
            del transition_params["text"]

        return super(DelegateTransitionExtender, self)._deserialize_schema(
            schema, transition_params, collect_errors=collect_errors)


@implementer(ITransitionExtender)
@adapter(ITask, IBrowserRequest)
class OpenPlannedTransitionExtender(DefaultTransitionExtender):
    """Default transition extender but supress default activity and
    record an TaskAdded activity instead."""

    def after_transition_hook(self, transition, disable_sync, transition_params):
        response = add_simple_response(self.context,
                                       transition=transition,
                                       text=transition_params.get('text'),
                                       supress_activity=True)

        TaskAddedActivity(
            self.context, getRequest()).record()

        self.save_related_items(response, transition_params.get('relatedItems'))
        self.sync_change(transition, transition_params.get('text'), disable_sync)
