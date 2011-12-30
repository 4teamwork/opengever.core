from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from five import grok
from ftw.pdfgenerator.browser.views import ExportPDFView
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.pdfgenerator.view import MakoLaTeXView
from ftw.table import helper
from opengever.latex.interfaces import ILandscapeLayer
from opengever.latex.utils import get_dossier_sequence_number_and_title
from opengever.latex.utils import get_selected_items
from opengever.ogds.base.interfaces import IContactInformation
from zope.component import getUtility
from zope.interface import Interface
from zope.interface import directlyProvidedBy, directlyProvides


class TaskListingPDFView(grok.View, ExportPDFView):
    grok.name('pdf-tasks-listing')
    grok.require('zope2.View')
    grok.context(Interface)

    index = ViewPageTemplateFile('templates/export_pdf.pt')

    def render(self):
        # let the request provide ILandscapeLayer
        if not ILandscapeLayer.providedBy(self.request):
            ifaces = [ILandscapeLayer,] + list(directlyProvidedBy(
                    self.request))
            directlyProvides(self.request, *ifaces)

        return ExportPDFView.__call__(self)


class TaskListingLaTeXView(grok.MultiAdapter, MakoLaTeXView):
    grok.provides(ILaTeXView)
    grok.adapts(Interface, ILandscapeLayer, ILaTeXLayout)

    template_directories = ['templates']
    template_name = 'tasklisting.tex'

    def get_render_arguments(self):
        self.layout.show_organisation = True
        self.info = getUtility(IContactInformation)

        return {'rows': self.get_rows()}

    def get_rows(self):
        rows = []

        for row in get_selected_items(self.context, self.request):
            rows.append(self.get_row_for_item(row))

        return rows

    def get_row_for_item(self, item):
        sequence_number = unicode(item.sequence_number).encode('utf-8')
        deadline = helper.readable_date(item, item.deadline)

        title = unicode(getattr(item, 'Title',
                            getattr(item, 'title', ''))).encode('utf-8')

        issuer_client_title = self.info.get_client_by_id(
            item.client_id).title
        issuer = '%s / %s' % (issuer_client_title,
                         self.info.describe(item.issuer))

        dossier_seq_num, dossier_title = \
            get_dossier_sequence_number_and_title(item)

        reference = unicode(getattr(
                item, 'reference',
                getattr(item, 'reference_number', ''))).encode('utf-8')

        data = [
            sequence_number,
            deadline,
            title,
            issuer,
            dossier_seq_num,
            dossier_title,
            reference,
            ]

        return self.convert_list_to_row(data)

    def convert_list_to_row(self, row):
        return ' & '.join([self.convert(cell) for cell in row])
