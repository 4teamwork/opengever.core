from opengever.dossier import  _
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from zope import schema
from zope.interface import Interface
from zope.interface import alsoProvides


class IFilingNumberMarker(Interface):
    """Marker interface for the filing number behavior"""


class IFilingNumber(form.Schema):

    form.fieldset(
        u'filing',
        label=_(u'fieldset_filing', default=u'Filing'),
        fields=['filing_no'],
        )

    form.omitted('filing_no')
    filing_no = schema.TextLine(
        title=_(u'filing_no', default="Filing number"),
        description=_(u'help_filing_no', default=u''),
        required=False,
        )


alsoProvides(IFilingNumber, IFormFieldProvider)
