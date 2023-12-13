from opengever.base.transition import ITransitionExtender
from opengever.inbox.browser.refuse import store_copy_in_remote_yearfolder
from opengever.inbox.forwarding import IForwarding
from opengever.ogds.base.sources import AllUsersInboxesAndTeamsSourceBinder
from opengever.ogds.base.utils import get_current_org_unit
from opengever.task import _ as task_mf
from opengever.task.interfaces import IYearfolderStorer
from opengever.task.transition import DefaultTransitionExtender
from opengever.task.transition import IResponse
from opengever.task.transition import ReassignTransitionExtender
from opengever.task.util import add_simple_response
from plone.supermodel.model import Schema
from zope import schema
from zope.component import adapter
from zope.event import notify
from zope.interface import implementer
from zope.lifecycleevent import ObjectModifiedEvent
from zope.publisher.interfaces.browser import IBrowserRequest


class ISuccessorSchema(Schema):
    successor_oguid = schema.TextLine()


@implementer(ITransitionExtender)
@adapter(IForwarding, IBrowserRequest)
class ForwardingDefaultTransitionExtender(DefaultTransitionExtender):
    """Default transition extender for all forwarding transitions."""


@implementer(ITransitionExtender)
@adapter(IForwarding, IBrowserRequest)
class ForwardingRefuseTransitionExtender(ForwardingDefaultTransitionExtender):
    """Transition Extender for forwardings close transition, stores forwarding
    to yearfolder after state change.
    """

    def after_transition_hook(self, transition, disable_sync, transition_params):
        add_simple_response(self.context, transition=transition,
                            text=transition_params.get('text'), supress_events=True)

        copy_url = store_copy_in_remote_yearfolder(self.context,
                                                   self.context.get_responsible_admin_unit().id())

        self.switch_responsible()
        notify(ObjectModifiedEvent(self.context))
        return {'location': copy_url}

    def switch_responsible(self):
        self.context.add_former_responsible(self.context.responsible)
        current_org_unit = get_current_org_unit()
        self.context.responsible_client = current_org_unit.id()
        self.context.responsible = current_org_unit.inbox().id()


@implementer(ITransitionExtender)
@adapter(IForwarding, IBrowserRequest)
class ForwardingCloseTransitionExtender(ForwardingDefaultTransitionExtender):
    """Transition Extender for forwardings close transition, stores forwarding
    to yearfolder after state change.
    """

    def after_transition_hook(self, transition, disable_sync, transition_params):
        add_simple_response(
            self.context, transition=transition, text=transition_params.get('text'))

        IYearfolderStorer(self.context).store_in_yearfolder()


@implementer(ITransitionExtender)
@adapter(IForwarding, IBrowserRequest)
class ForwardingAssignToDossierTransitionExtender(ForwardingDefaultTransitionExtender):
    """Transition extender for forwarding closing
    """

    schemas = [IResponse, ISuccessorSchema]

    def after_transition_hook(self, transition, disable_sync, transition_params):
        add_simple_response(
            self.context, transition=transition, text=transition_params.get('text'),
            successor_oguid=transition_params.get('successor_oguid'))

        IYearfolderStorer(self.context).store_in_yearfolder()


class INewForwardingResponsibleSchema(Schema):
    responsible = schema.Choice(
        title=task_mf(u"label_responsible", default=u"Responsible"),
        description=task_mf(u"help_responsible", default=""),
        source=AllUsersInboxesAndTeamsSourceBinder(include_teams=True),
        required=True,
    )

    responsible_client = schema.Choice(
        title=task_mf(u'label_resonsible_client', default=u'Responsible Client'),
        description=task_mf(u'help_responsible_client', default=u''),
        vocabulary='opengever.ogds.base.OrgUnitsVocabularyFactory',
        required=True)


@implementer(ITransitionExtender)
@adapter(IForwarding, IBrowserRequest)
class ForwardingReassignTransitionExtender(ReassignTransitionExtender):
    """Transition extender for forwarding reassign transition."""

    schemas = [IResponse, INewForwardingResponsibleSchema]
