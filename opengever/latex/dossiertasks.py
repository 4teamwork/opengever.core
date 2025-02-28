from contextlib import contextmanager
from ftw.pdfgenerator.browser.views import ExportPDFView
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import IPDFAssembler
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.pdfgenerator.view import MakoLaTeXView
from opengever.base.response import IResponseContainer
from opengever.latex import _
from opengever.latex.listing import ILaTexListing
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

        title = self.convert_plain(title)

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

            task_description = task.text.output if task.text else u''

            task_data_list.append({
                'title': self.convert_plain(task.title),
<<<<<<< HEAD
<<<<<<< HEAD
                'description': self.convert(task_description),
=======
                'description': self.convert_plain(task.text.output or ""),
>>>>>>> ec7aadd6e (Change text field in task schema to RichField and serialize after first)
=======
                'description': self.convert_plain(task.text or ""),
>>>>>>> 68b194d98 (Set default "" string)
                'sequence_number': task.get_sequence_number(),
                'type': self.convert_plain(task.get_task_type_label()),
                'completion_date': completion_date,
                'deadline': deadline,
                'responsible': self.convert_plain(task.get_responsible_actor().get_label()),
                'issuer': self.convert_plain(task.get_issuer_actor().get_label()),
                'history': task_history.get_listing(response_container),
            })

        return {'task_data_list': task_data_list,
                'label': title}

    def get_tasks(self):
        task_brains = api.content.find(context=self.context, object_provides=ITask)
        tasks = [el.getObject() for el in task_brains]
        tasks.sort(key=lambda task: task.get_sequence_number())
        return tasks
