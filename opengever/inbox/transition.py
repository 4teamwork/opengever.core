from opengever.activity import notification_center
from opengever.base.oguid import Oguid
from opengever.base.source import RepositoryPathSourceBinder
from opengever.base.transition import ITransitionExtender
from opengever.inbox import _
from opengever.inbox.forwarding import IForwarding
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import get_current_org_unit
from opengever.task.browser.accept.utils import _copy_documents_from_forwarding
from opengever.task.browser.accept.utils import FORWARDING_SUCCESSOR_TYPE
from opengever.task.interfaces import ISuccessorTaskController
from opengever.task.interfaces import IYearfolderStorer
from opengever.task.task import ITask
from opengever.task.transition import DefaultTransitionExtender
from opengever.task.transition import IResponse
from opengever.task.transition import ReassignTransitionExtender
from opengever.task.transporter import IResponseTransporter
from opengever.task.util import add_simple_response
from plone.dexterity.utils import createContentInContainer
from plone.supermodel.model import Schema
from z3c.relationfield.schema import RelationChoice
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


class IChooseDossierSchema(Schema):

    dossier = RelationChoice(
        title=_(u'label_dossier', default=u'Dossier'),
        source=RepositoryPathSourceBinder(
            object_provides='opengever.dossier.behaviors.dossier.'
            'IDossierMarker',
            navigation_tree_query={
                'object_provides': [
                    'opengever.repository.repositoryroot.IRepositoryRoot',
                    'opengever.repository.repositoryfolder.'
                    'IRepositoryFolderSchema',
                    'opengever.dossier.behaviors.dossier.IDossierMarker',
                ]
                }),
        required=False)


@implementer(ITransitionExtender)
@adapter(IForwarding, IBrowserRequest)
class ForwardingDefaultTransitionExtender(DefaultTransitionExtender):
    """Default transiition extender for all forwarding transitions."""


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

    schemas = [IResponse, IChooseDossierSchema]

    def after_transition_hook(self, transition, disable_sync, transition_params):
        successor_task = self.create_successor_task(transition_params['dossier'])

        add_simple_response(
            self.context, transition=transition, text=transition_params.get('text'),
            successor_oguid=Oguid.for_object(successor_task).id)

        # set predecessor on successor task
        successor_tc_task = ISuccessorTaskController(successor_task)
        successor_tc_task.set_predecessor(Oguid.for_object(self.context).id)

        IYearfolderStorer(self.context).store_in_yearfolder()
        return successor_task

    def create_successor_task(self, dossier):
        # we need all task field values from the forwarding
        fielddata = {}
        for fieldname in ITask.names():
            value = ITask.get(fieldname).get(self.context)
            fielddata[fieldname] = value

        # Reset issuer to the current inbox
        fielddata['issuer'] = get_current_org_unit().inbox().id()

        # Predefine the task_type to avoid tasks with an invalid task_type
        fielddata['task_type'] = FORWARDING_SUCCESSOR_TYPE

        # lets create a new task - the successor task
        task = createContentInContainer(
            dossier, 'opengever.task.task', **fielddata)

        # Add issuer and responsible to the watchers of the newly created task
        center = notification_center()
        center.add_task_responsible(task, task.responsible)
        center.add_task_issuer(task, task.issuer)

        # copy documents and map the intids
        intids_mapping = _copy_documents_from_forwarding(self.context, task)

        # copy the responses
        response_transporter = IResponseTransporter(task)
        response_transporter.get_responses(
            get_current_admin_unit().id(),
            '/'.join(self.context.getPhysicalPath()),
            intids_mapping=intids_mapping)

        return task


@implementer(ITransitionExtender)
@adapter(IForwarding, IBrowserRequest)
class ForwardingReassignTransitionExtender(ReassignTransitionExtender):
    """Transition extender for forwarding reassign transition."""
