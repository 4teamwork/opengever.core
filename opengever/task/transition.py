from opengever.base.transition import ITransitionExtender
from opengever.base.transition import TransitionExtender
from opengever.ogds.base.sources import AllUsersInboxesAndTeamsSourceBinder
from opengever.task import _
from opengever.task.activities import TaskReassignActivity
from opengever.task.interfaces import IDeadlineModifier
from opengever.task.response_syncer import sync_task_response
from opengever.task.task import ITask
from opengever.task.util import add_simple_response
from plone.supermodel.model import Schema
from zope import schema
from zope.component import adapter
from zope.event import notify
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.lifecycleevent import ObjectModifiedEvent


class IResponse(Schema):

    text = schema.Text(
        title=_('label_response', default="Response"),
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

    def after_transition_hook(self, transition, **kwargs):
        add_simple_response(
            self.context, transition=transition, text=kwargs.get('text'))


@implementer(ITransitionExtender)
@adapter(ITask)
class AcceptTransitionExtender(TransitionExtender):

    schemas = [IResponse, ]

    def after_transition_hook(self, transition, **kwargs):
        add_simple_response(
            self.context, transition=transition, text=kwargs.get('text'))


@implementer(ITransitionExtender)
@adapter(ITask)
class ModifyDeadlineTransitionExtender(TransitionExtender):

    schemas = [INewDeadline, ]

    def after_transition_hook(self, transition, **kwargs):
        IDeadlineModifier(self.context).modify_deadline(
            kwargs['new_deadline'], kwargs.get('text'), transition)


@implementer(ITransitionExtender)
@adapter(ITask)
class ResolveTransitionExtender(TransitionExtender):

    schemas = [IResponse, ]

    def after_transition_hook(self, transition, **kwargs):
        add_simple_response(
            self.context, transition=transition, text=kwargs.get('text'))


@implementer(ITransitionExtender)
@adapter(ITask)
class CloseTransitionExtender(TransitionExtender):

    schemas = [IResponse, ]

    def after_transition_hook(self, transition, **kwargs):
        add_simple_response(
            self.context, transition=transition, text=kwargs.get('text'))


@implementer(ITransitionExtender)
@adapter(ITask)
class ReassignTransitionExtender(TransitionExtender):

    schemas = [IResponse, INewResponsibleSchema]

    def after_transition_hook(self, transition, **kwargs):
        former_responsible = ITask['responsible']
        former_responsible_client = ITask['responsible_client']

        changes =(
            (former_responsible, kwargs.get('responsible')),
            (former_responsible_client, kwargs.get('responsible_client')))
        response = add_simple_response(
            self.context, transition=transition, text=kwargs.get('text'),
            field_changes=changes, supress_events=True)

        self.change_responsible(**kwargs)
        notify(ObjectModifiedEvent(self.context))
        self.record_activity(response)

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
