from five import grok
from plone.directives import dexterity

from opengever.dossier.behaviors.dossier import IDossierMarker, IDossier
from Products.CMFCore.utils import getToolByName
from opengever.dossier.latex.dossierlayout import DossierLayout

from plone.autoform.base import AutoFields

from plonegov.pdflatex.browser.converter import LatexCTConverter

class DossierView(dexterity.DisplayForm):
    grok.context(IDossierMarker)
    grok.require('zope2.View')
    def responsible(self):
        mt=getToolByName(self.context,'portal_membership')
        dossier = IDossier(self.context)
        return mt.getMemberById(dossier.responsible).getProperty('fullname',dossier.responsible)
        
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
        return as_pdf(**arguments)

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

    def __call__(self, context, view):
        self.view = view
        latex = '\\section*{%s}\n' % self.context.Title()
        latex = latex.encode('utf8')
        table = context.restrictedTraverse("@@dossierview")()
        latex += self.view.convert(table)
        return latex