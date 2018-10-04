from opengever.activity import notification_center
from opengever.activity.roles import TASK_RESPONSIBLE_ROLE
from opengever.base.source import DossierPathSourceBinder
from opengever.base.transition import ITransitionExtender
from opengever.base.transition import TransitionExtender
from opengever.ogds.base.sources import AllUsersInboxesAndTeamsSourceBinder
from opengever.task import _
from opengever.task.activities import TaskReassignActivity
from opengever.task.browser.delegate.metadata import IUpdateMetadata
from opengever.task.browser.delegate.recipients import ISelectRecipientsSchema
from opengever.task.browser.delegate.utils import create_subtasks
from opengever.task.interfaces import IDeadlineModifier
from opengever.task.localroles import LocalRolesSetter
from opengever.task.reminder.reminder import TaskReminder
from opengever.task.response_syncer import sync_task_response
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
from plone.supermodel.model import Schema
from z3c.relationfield.relation import RelationValue
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.component import adapter
from zope.component import getUtility
from zope.event import notify
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectModifiedEvent


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


@implementer(ITransitionExtender)
@adapter(ITask)
class DefaultTransitionExtender(TransitionExtender):

    schemas = [IResponse, ]

    def after_transition_hook(self, transition, disable_sync, **kwargs):
        response = add_simple_response(
            self.context, transition=transition, text=kwargs.get('text'))

        self.save_related_items(response, kwargs.get('relatedItems'))
        self.sync_change(transition, kwargs.get('text'), disable_sync)

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
@adapter(ITask)
class AcceptTransitionExtender(DefaultTransitionExtender):

    schemas = [IResponse, ]

    def after_transition_hook(self, transition, disable_sync, **kwargs):
        response = add_simple_response(
            self.context, transition=transition, text=kwargs.get('text'))

        self.save_related_items(response, kwargs.get('relatedItems'))
        self.sync_change(transition, kwargs.get('text'), disable_sync)


@implementer(ITransitionExtender)
@adapter(ITask)
class ModifyDeadlineTransitionExtender(TransitionExtender):

    schemas = [INewDeadline, ]

    def after_transition_hook(self, transition, disable_sync, **kwargs):
        IDeadlineModifier(self.context).modify_deadline(
            kwargs['new_deadline'], kwargs.get('text'), transition)


@implementer(ITransitionExtender)
@adapter(ITask)
class ResolveTransitionExtender(DefaultTransitionExtender):

    schemas = [IResponse, ]

    def after_transition_hook(self, transition, disable_sync, **kwargs):
        response = add_simple_response(
            self.context, transition=transition, text=kwargs.get('text'))

        self.save_related_items(response, kwargs.get('relatedItems'))
        self.sync_change(transition, kwargs.get('text'), disable_sync)


@implementer(ITransitionExtender)
@adapter(ITask)
class CloseTransitionExtender(DefaultTransitionExtender):

    schemas = [IResponse, ]

    def after_transition_hook(self, transition, disable_sync, **kwargs):
        response = add_simple_response(
            self.context, transition=transition, text=kwargs.get('text'))

        self.save_related_items(response, kwargs.get('relatedItems'))
        self.sync_change(transition, kwargs.get('text'), disable_sync)


@implementer(ITransitionExtender)
@adapter(ITask)
class ReassignTransitionExtender(DefaultTransitionExtender):

    schemas = [IResponse, INewResponsibleSchema]

    def after_transition_hook(self, transition, disable_sync, **kwargs):
        # Revoke local roles for current responsible the roles for the
        # new responsible will be assigned afterwards
        LocalRolesSetter(self.context).revoke_roles()

        former_responsible = ITask['responsible']
        former_responsible_client = ITask['responsible_client']

        TaskReminder().clear_reminder(self.context, self.context.responsible)

        changes = (
            (former_responsible, kwargs.get('responsible')),
            (former_responsible_client, kwargs.get('responsible_client')))
        response = add_simple_response(
            self.context, transition=transition, text=kwargs.get('text'),
            field_changes=changes, supress_events=True)

        self.save_related_items(response, kwargs.get('relatedItems'))
        self.change_responsible(**kwargs)
        notify(ObjectModifiedEvent(self.context))
        self.record_activity(response)

        if not disable_sync:
            sync_task_response(self.context, getRequest(), 'workflow',
                               transition,
                               kwargs.get('text'),
                               responsible=kwargs.get('responsible'),
                               responsible_client=kwargs.get('responsible_client'))

    def change_responsible(self, **kwargs):
        self.context.responsible_client = kwargs.get('responsible_client')
        self.context.responsible = kwargs.get('responsible')

    def record_activity(self, response):
        TaskReassignActivity(self.context, self.context.REQUEST, response).record()


@implementer(ITransitionExtender)
@adapter(ITask)
class RejectTransitionExtender(DefaultTransitionExtender):
    """Default task transition handling expect the responsible is switched
    to task's issuer.
    """

    schemas = [IResponse, ]

    def after_transition_hook(self, transition, disable_sync, **kwargs):
        self.update_watchers()

        response = add_simple_response(
            self.context, transition=transition, text=kwargs.get('text'))

        response.add_change(
            'responsible',
            _(u"label_responsible", default=u"Responsible"),
            ITask(self.context).responsible, ITask(self.context).issuer)

        self.save_related_items(response, kwargs.get('relatedItems'))
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
@adapter(ITask)
class DelegateTransitionExtender(DefaultTransitionExtender):

    schemas = [IUpdateMetadata, ISelectRecipientsSchema]

    def after_transition_hook(self, transition, disable_sync, **kwargs):
        create_subtasks(self.context,
                        kwargs.pop('responsibles'),
                        kwargs.get('documents', []), kwargs)
