from contextlib import contextmanager
from ftw.pdfgenerator.browser.views import ExportPDFView
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import IPDFAssembler
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.pdfgenerator.view import MakoLaTeXView
from opengever.latex import _
from opengever.latex.listing import ILaTexListing
from opengever.task.adapters import IResponseContainer
from opengever.task.task import ITask
from plone import api
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.i18n import translate
from zope.interface import Interface
from zope.interface import noLongerProvides


class IDossierTasksLayer(Interface):
    """Request layer for selecting the dossier tasks view.
    """


@contextmanager
def provide_dossier_task_layer(request):
    try:
        provide_request_layer(request, IDossierTasksLayer)
        yield
    finally:
        noLongerProvides(request, IDossierTasksLayer)


class DossierTasksPDFView(ExportPDFView):

    def __call__(self):
        # Enable IDossierTasksLayer
        with provide_dossier_task_layer(self.request):
            return super(DossierTasksPDFView, self).__call__()

    def get_data(self):
        # let the request provide IDossierTasksLayer
        with provide_dossier_task_layer(self.request):
            assembler = getMultiAdapter((self.context, self.request),
                                        IPDFAssembler)
            return assembler.build_pdf()


@adapter(Interface, IDossierTasksLayer, ILaTeXLayout)
class DossierTasksLaTeXView(MakoLaTeXView):

    template_directories = ['templates']
    template_name = 'dossiertasks.tex'
    strftimestring = '%d.%m.%Y'

    def get_render_arguments(self):
        self.layout.show_organisation = True

        tasks = self.get_tasks()
        task_data_list = []
        title = translate(_('label_dossier_tasks',
                            default=u'Task list for dossier "${title} (${reference_number})"',
                          mapping={'title': self.context.title,
                                   'reference_number': self.context.get_reference_number()}),
                          context=self.request)

        for task in tasks:
            task_history = getMultiAdapter((task, self.request, self),
                                           ILaTexListing, name='task-history')

            response_container = IResponseContainer(task)

            completion_date = task.date_of_completion
            if completion_date:
                completion_date = completion_date.strftime(self.strftimestring)

            deadline = task.deadline
            if deadline:
                deadline = deadline.strftime(self.strftimestring)

            task_data_list.append({'title': task.title,
                                   'description': task.text or "",
                                   'sequence_number': task.get_sequence_number(),
                                   'type': task.get_task_type_label(),
                                   'completion_date': completion_date,
                                   'deadline': deadline,
                                   'responsible': task.get_responsible_actor().get_label(),
                                   'issuer': task.get_issuer_actor().get_label(),
                                   'history': task_history.get_listing(response_container)})

        return {'task_data_list': task_data_list,
                'label': title}

    def get_tasks(self):
        task_brains = api.content.find(context=self.context, object_provides=ITask)
        tasks = [el.getObject() for el in task_brains]
        tasks.sort(key=lambda task: task.get_sequence_number())
        return tasks
