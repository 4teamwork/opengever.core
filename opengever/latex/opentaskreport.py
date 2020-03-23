from ftw.pdfgenerator.browser.views import ExportPDFView
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.pdfgenerator.view import MakoLaTeXView
from ftw.table import helper
from opengever.base.model import Session
from opengever.globalindex.model.task import Task
from opengever.latex.interfaces import ILandscapeLayer
from opengever.latex.utils import get_issuer_of_task
from opengever.latex.utils import workflow_state
from opengever.ogds.base.actor import Actor
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import get_current_org_unit
from opengever.ogds.models.service import ogds_service
from opengever.task.helper import task_type_helper
from Products.Five import BrowserView
from sqlalchemy import and_
from sqlalchemy import or_
from sqlalchemy.sql.expression import asc
from zExceptions import Unauthorized
from zope.component import adapter
from zope.interface import Interface


OPEN_TASK_STATES = [
    'task-state-open',
    'task-state-in-progress',
    'task-state-resolved',
    'task-state-rejected',
    'forwarding-state-open',
]


class IOpenTaskReportLayer(ILandscapeLayer):
    """Request layer for selecting the open task report view.
    """


class OpenTaskReportPDFView(ExportPDFView):

    request_layer = IOpenTaskReportLayer

    def __call__(self):
        if not is_open_task_report_allowed():
            raise Unauthorized()

        provide_request_layer(self.request, self.request_layer)
        return super(OpenTaskReportPDFView, self).__call__()


@adapter(Interface, IOpenTaskReportLayer, ILaTeXLayout)
class OpenTaskReportLaTeXView(MakoLaTeXView):

    template_directories = ['templates']
    template_name = 'opentaskreport.tex'

    def get_render_arguments(self):
        self.layout.show_organisation = True
        self.layout.use_package('longtable')

        args = self.get_task_rows()
        args['client'] = get_current_org_unit().label()

        return args

    def _extend_task_query(self, query):
        """Extends a globalindex task query.
        """
        # sort by deadline
        query = query.order_by(asc(Task.deadline))

        # list only open tasks
        query = query.filter(Task.review_state.in_(OPEN_TASK_STATES))

        # If a task has a successor task, list only one of them.
        # List only the one which is assigned to this client.
        query = query.filter(
            or_(
                and_(Task.predecessor == None, Task.successors == None),  # noqa: comparison to None is correct for SQLAlchemy
                Task.admin_unit_id == get_current_admin_unit().id()))

        return query

    def get_task_rows(self):
        """Returns a dict of task-rows (tuples of cells) of all open tasks on
        the current client:

        incoming -- open tasks assigned to the current client
        outgoing -- open tasks assigned to another client
        """
        org_unit_id = get_current_org_unit().id()

        incoming_query = Session().query(Task)
        incoming_query = incoming_query.filter(
            Task.assigned_org_unit == org_unit_id)
        incoming_query = self._extend_task_query(incoming_query)

        incoming = []
        for task in incoming_query.all():
            incoming.append(self.get_row_for_item(
                            task,
                            display_issuing_org_unit=True))

        outgoing_query = Session().query(Task)
        outgoing_query = outgoing_query.filter(
            Task.issuing_org_unit == org_unit_id)
        outgoing_query = self._extend_task_query(outgoing_query)

        outgoing = []
        for task in outgoing_query.all():
            outgoing.append(self.get_row_for_item(
                task, display_assigned_org_unit=True))

        return {'incoming': incoming,
                'outgoing': outgoing}

    def get_row_for_item(self, item, display_issuing_org_unit=False,
                         display_assigned_org_unit=False):
        return self.convert_list_to_row(
            self.get_data_for_item(
                item,
                display_issuing_org_unit=display_issuing_org_unit,
                display_assigned_org_unit=display_assigned_org_unit))

    def get_data_for_item(self, item,
                          display_issuing_org_unit=False,
                          display_assigned_org_unit=False):
        task_type = task_type_helper(item, item.task_type)
        sequence_number = unicode(item.sequence_number).encode('utf-8')
        deadline = helper.readable_date(item, item.deadline)

        title = unicode(getattr(item, 'Title',
                        getattr(item, 'title', ''))).encode('utf-8')

        issuer = get_issuer_of_task(item,
                                    with_client=display_issuing_org_unit,
                                    with_principal=False)

        actor = Actor.lookup(item.responsible)
        responsible = actor.get_label(with_principal=False)

        if display_assigned_org_unit:
            org_unit = item.get_assigned_org_unit()
            responsible = org_unit.prefix_label(responsible)

        dossier_title = item.containing_dossier or ''

        reference = unicode(getattr(
            item, 'reference',
            getattr(item, 'reference_number', ''))).encode('utf-8')

        review_state = workflow_state(item, item.review_state)

        return [
            sequence_number,
            title,
            task_type,
            dossier_title,
            reference,
            issuer,
            responsible,
            deadline,
            review_state,
        ]

    def convert_list_to_row(self, row):
        return ' & '.join([self.convert_plain(cell) for cell in row])


class OpenTaskReportPDFAllowed(BrowserView):

    def __call__(self):
        return is_open_task_report_allowed()


def is_open_task_report_allowed():
    inbox = get_current_org_unit().inbox()
    return ogds_service().fetch_current_user() in inbox.assigned_users()
