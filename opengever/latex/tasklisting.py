from ftw.pdfgenerator.browser.views import ExportPDFView
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.pdfgenerator.view import MakoLaTeXView
from ftw.table import helper
from opengever.globalindex.utils import get_selected_items
from opengever.latex.interfaces import ILandscapeLayer
from opengever.latex.utils import get_issuer_of_task
from opengever.latex.utils import workflow_state
from opengever.ogds.base.actor import Actor
from opengever.task.helper import task_type_helper
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapter
from zope.interface import Interface


class ITaskListingLayer(ILandscapeLayer):
    """Task listing request layer.
    - Select landsacpe layout by subclassing ILandscapeLayer
    - Select view
    """


class TaskListingPDFView(ExportPDFView):

    index = ViewPageTemplateFile('templates/export_pdf.pt')

    request_layer = ITaskListingLayer

    def __call__(self):
        # let the request provide ITaskListingLayer
        provide_request_layer(self.request, self.request_layer)

        return super(TaskListingPDFView, self).__call__()


@adapter(Interface, ITaskListingLayer, ILaTeXLayout)
class TaskListingLaTeXView(MakoLaTeXView):

    template_directories = ['templates']
    template_name = 'tasklisting.tex'

    def __init__(self, *args, **kwargs):
        MakoLaTeXView.__init__(self, *args, **kwargs)
        self.info = None

    def get_render_arguments(self):
        self.layout.show_organisation = True

        return {'rows': self.get_rows()}

    def get_rows(self):
        rows = []

        for row in get_selected_items(self.context, self.request):
            rows.append(self.get_row_for_item(row))

        return rows

    def get_data_for_item(self, item):
        admin_unit = item.get_admin_unit().abbreviation
        task_type = task_type_helper(item, item.task_type)
        sequence_number = unicode(item.sequence_number).encode('utf-8')
        deadline = helper.readable_date(item, item.deadline)

        title = unicode(getattr(item, 'Title',
                        getattr(item, 'title', ''))).encode('utf-8')

        issuer = get_issuer_of_task(item, with_client=True, with_principal=False)

        responsible_org_unit = item.get_assigned_org_unit()
        responsible = Actor.lookup(item.responsible)
        responsible_label = responsible_org_unit.prefix_label(
            responsible.get_label(with_principal=False))

        dossier_title = item.containing_dossier or ''

        main_task_title = item.get_main_task_title() or ''

        reference = unicode(
            getattr(item, 'reference',
                    getattr(item, 'reference_number', ''))).encode('utf-8')

        review_state = workflow_state(item, item.review_state)

        return [
            admin_unit,
            sequence_number,
            title,
            task_type,
            dossier_title,
            main_task_title,
            reference,
            issuer,
            responsible_label,
            deadline,
            review_state,
        ]

    def get_row_for_item(self, item):
        return self.convert_list_to_row(self.get_data_for_item(item))

    def convert_list_to_row(self, row):
        return ' & '.join([self.convert_plain(cell) for cell in row])
