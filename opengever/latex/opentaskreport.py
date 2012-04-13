from five import grok
from ftw.pdfgenerator.browser.views import ExportPDFView
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.pdfgenerator.view import MakoLaTeXView
from ftw.table import helper
from opengever.globalindex import Session
from opengever.globalindex.model.task import Task
from opengever.latex.interfaces import ILandscapeLayer
from opengever.latex.utils import get_issuer_of_task
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_client_id, get_current_client
from opengever.tabbedview.helper import workflow_state
from opengever.task.helper import task_type_helper
from sqlalchemy import and_, or_
from sqlalchemy.sql.expression import asc
from zope.component import getUtility
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


class OpenTaskReportPDFView(grok.View, ExportPDFView):
    grok.name('pdf-open-task-report')
    grok.context(Interface)
    grok.require('zope2.View')

    def render(self):
        provide_request_layer(self.request, IOpenTaskReportLayer)

        return ExportPDFView.__call__(self)


class OpenTaskReportLaTeXView(grok.MultiAdapter, MakoLaTeXView):
    grok.provides(ILaTeXView)
    grok.adapts(Interface, IOpenTaskReportLayer, ILaTeXLayout)

    template_directories = ['templates']
    template_name = 'opentaskreport.tex'

    def get_render_arguments(self):
        self.info = getUtility(IContactInformation)

        self.layout.show_organisation = True
        self.layout.use_package('longtable')

        args = self.get_task_rows()
        args['client'] = get_current_client().title

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
                and_(Task.predecessor == None, Task.successors == None),
                Task.client_id == get_client_id()))

        return query

    def get_task_rows(self):
        """Returns a dict of task-rows (tuples of cells) of all open tasks on
        the current client:

        incoming -- open tasks assigned to the current client
        outgoing -- open tasks assigned to another client
        """

        clientid = get_client_id()

        incoming_query = Session().query(Task)
        incoming_query = incoming_query.filter(
            Task.assigned_client == clientid)
        incoming_query = self._extend_task_query(incoming_query)

        incoming = []
        for task in incoming_query.all():
            incoming.append(self.get_row_for_item(
                    task,
                    display_issuer_client=True))

        outgoing_query = Session().query(Task)
        outgoing_query = outgoing_query.filter(Task.client_id == clientid)
        outgoing_query = self._extend_task_query(outgoing_query)

        outgoing = []
        for task in outgoing_query.all():
            outgoing.append(self.get_row_for_item(
                    task, display_responsible_client=True))

        return {'incoming': incoming,
                'outgoing': outgoing}

    def get_row_for_item(self, item, display_issuer_client=False,
                         display_responsible_client=False):
        task_type = task_type_helper(item, item.task_type)
        sequence_number = unicode(item.sequence_number).encode('utf-8')
        deadline = helper.readable_date(item, item.deadline)

        title = unicode(getattr(item, 'Title',
                            getattr(item, 'title', ''))).encode('utf-8')

        issuer = get_issuer_of_task(item,
                                    with_client=display_issuer_client,
                                    with_principal=False)

        responsible = self.info.describe(item.responsible,
                                         with_principal=False)

        if display_responsible_client:
            responsible_client = self.info.get_client_by_id(
                item.assigned_client).title
            responsible = '%s / %s' % (
                responsible_client,
                responsible)

        dossier_title = item.containing_dossier or ''

        reference = unicode(getattr(
                item, 'reference',
                getattr(item, 'reference_number', ''))).encode('utf-8')

        review_state = workflow_state(item, item.review_state)

        data = [
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

        return self.convert_list_to_row(data)

    def convert_list_to_row(self, row):
        return ' & '.join([self.convert(cell) for cell in row])


class OpenTaskReportPDFAllowed(grok.View):
    grok.name('pdf-open-task-report-allowed')
    grok.context(Interface)
    grok.require('zope2.View')

    def render(self):
        info = getUtility(IContactInformation)
        return info.is_user_in_inbox_group()
