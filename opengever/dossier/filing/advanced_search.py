from five import grok
from opengever.advancedsearch import _
from opengever.advancedsearch.advanced_search import AdvancedSearchForm
from opengever.advancedsearch.advanced_search import IAdvancedSearch
from opengever.dossier.filing.interfaces import IFilingNumberActivatedLayer
from plone.directives import form as directives_form
from plone.z3cform.fieldsets.utils import move
from zope import schema
from zope.interface import Interface


class IFilingnumberSearchAddition(directives_form.Schema):

    searchable_filing_no = schema.TextLine(
        title=_('label_filing_number', default='Filing number'),
        description=_('help_filing_number', default=''),
        required=False,
    )


class FilingAdvancedSearchForm(AdvancedSearchForm):
    grok.context(Interface)
    grok.name('advanced_search')
    grok.require('zope2.View')
    grok.layer(IFilingNumberActivatedLayer)

    schemas = (IAdvancedSearch, IFilingnumberSearchAddition)

    def move_fields(self):
        move(self, 'searchable_filing_no', before='responsible')

    def field_mapping(self):
        """Append searchable_filing_no to default field mappings"""

        mapping = super(FilingAdvancedSearchForm, self).field_mapping()
        dossier_fields = mapping.get(
            'opengever-dossier-behaviors-dossier-IDossierMarker')

        if 'searchable_filing_no' not in dossier_fields:
            dossier_fields.insert(
                dossier_fields.index('responsible'), 'searchable_filing_no')

        return mapping
