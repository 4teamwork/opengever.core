from five import grok
from Acquisition import aq_inner, aq_parent

from opengever.dossier.behaviors.dossier import IDossierMarker, IDossier
from Products.statusmessages.interfaces import IStatusMessage
from opengever.latex import _
from opengever.latex.layouts.dossierlayout import DossierLayout
from opengever.ogds.base.interfaces import IContactInformation
from opengever.repository.interfaces import IRepositoryFolder

from zope.component import getUtility, getAdapter
from zope.schema.vocabulary import getVocabularyRegistry
from opengever.base.interfaces import IReferenceNumber, ISequenceNumber
from zope.component import queryUtility
from plone.registry.interfaces import IRegistry
from opengever.base.interfaces import IBaseClientID
from plone.autoform.base import AutoFields

from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from plonegov.pdflatex.pdfgenerator import PdfMissingException
from plonegov.pdflatex.browser.converter import LatexCTConverter

class ExportPDFView(grok.CodeView):
    grok.context(IDossierMarker)
    grok.name('export_pdf')

    def render(self):
        arguments = {
            'default_book_settings' : False,
            'pre_compiler': pre_compiler,
        }
        as_pdf = self.context.restrictedTraverse(
            '%s/as_pdf' % '/'.join(self.context.getPhysicalPath())
        )
        try:
            pdf = as_pdf(**arguments)
        except PdfMissingException:
            # happens with arabic letters
            msg = _(u'pdf_generation_failed', default=u'The pdf generation process failed.')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return self.request.RESPONSE.redirect(self.context.absolute_url())
        return pdf

def pre_compiler(view, object):
    layout = DossierLayout()
    layout(view, object)

class DossierLatexConverter(LatexCTConverter,grok.CodeView,AutoFields):
    grok.name("pdflatex_convert_object")
    grok.context(IDossierMarker)
    grok.require('zope2.View')

    def render(self):
        pass

    def getDisplayListValue(self, object, fieldname):
        context = object.aq_inner
        field = context.getField(fieldname)
        vocab = field.Vocabulary(context)
        value = field.get(context)
        return context.displayValue(vocab, value)

    def getDisplayListValueFromDataGridField(self, object, fieldname, row, column_id):
        context = object.aq_inner
        field = context.getField(fieldname)
        widget = field.widget
        column_definition = widget.getColumnDefinition(field, column_id)
        vocab = column_definition.getVocabulary(context)
        cell_value = row.get(column_id)
        value = vocab.getValue(cell_value)
        return value and value or cell_value

    def getOwnerMember(self):
        creator_id = self.context.Creator()
        return self.context.portal_membership.getMemberById(creator_id)

    def responsible(self):
        dossier = IDossier(self.context)
        return dossier.responsible

    def __call__(self, context, view):
        parent = aq_parent(aq_inner(context))
        repositoryfolder = parent.portal_type=='opengever.repository.repositoryfolder' and parent.Title() or aq_parent(parent).Title()

        start = self.context.toLocalizedTime(str(IDossier(context).start))
        end = self.context.toLocalizedTime(str(IDossier(context).end))
        start = start==None and '-' or start
        end = end==None and '-' or end
        registry = queryUtility(IRegistry)
        proxy = registry.forInterface(IBaseClientID)
        
        # buildout a kind of breadcrumbs with all parental repository folders
        repository = []
        while not IPloneSiteRoot.providedBy(parent):
            if IRepositoryFolder.providedBy(parent):
                repository.append(parent.Title())
            parent = aq_parent(aq_inner(parent))

        # filing_prefix
        # Get the value and not the key from the prefix vocabulary
        filing_prefix = getVocabularyRegistry().get(
            self.context, 'opengever.dossier.type_prefixes').by_token.get(
                IDossier(self.context).filing_prefix).title

        filling_no = getattr(IDossier(context), 'filing_no', None)
        self.view = view
        latex = '\\linespread {1.5}\n'
        latex += '\\thispagestyle{empty}\n'
        latex += '\\noindent\n'
        latex += '\\small %s \\newline\n' % self.view.convert(proxy.client_id)
        latex += '\\noindent\n'
        latex += '\\includegraphics{strich} \\newline\n'
        latex += '\\scriptsize'
        latex += '\\hspace{0.15cm}Ordnungsposition: %s\\newline\n' % self.view.convert(' / '.join(repository))
        latex += '\\hspace{0.15cm}Aktenzeichen: %s\\newline\n' % self.view.convert(getAdapter(self.context, IReferenceNumber).get_number())
        if filing_prefix:
            latex += '\\hspace{0.15cm}Ablage: %s\\newline\n' % self.view.convert(filing_prefix)
        if filling_no:
            latex += '\\hspace{0.15cm}Ablagenummer: %s\\newline\n' % self.view.convert(filling_no)

        latex += '\\hspace{0.15cm}Laufnummer: %s\n' % self.view.convert(str(getUtility(ISequenceNumber).get_number(self.context)))
        latex += '\\noindent\n'
        latex += '\\vspace{0.8cm} \\newline\n'
        latex += '\\scriptsize %s\n' % self.view.convert(repositoryfolder)
        latex += '\\vspace{0.3cm} \\newline\n'
        latex += '\\small \\textbf{%s}. %s \\newline\n' %(self.view.convert(context.Title()),self.view.convert(context.Description()))
        latex += '\\vspace{0.3cm} \\newline\n'
        cinfo = getUtility(IContactInformation)
        responsible_name = cinfo.describe(self.responsible())
        latex += '\\scriptsize %s: %s\n' % (self.view.convert('Federf&uuml;hrung'),
                                            self.view.convert(responsible_name))
        latex += '\\vspace{0.15cm} \\newline\n'
        latex += 'Beginn: %s\\hspace{0.15cm}|\\hspace{0.15cm}\n' % self.view.convert(start)
        latex += 'Abschluss: %s\\hspace{0.15cm} \\newline\n' % self.view.convert(end)
        return latex
