from opengever.dossier import _
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import alsoProvides
from zope.interface import Interface


class IFilingNumberMarker(Interface):
    """Marker interface for the filing number behavior"""


class IFilingNumber(model.Schema):

    model.fieldset(
        u'filing',
        label=_(u'fieldset_filing', default=u'Filing'),
        fields=['filing_no'],
    )

    form.omitted('filing_no')
    filing_no = schema.TextLine(
        title=_(u'filing_no', default="Filing number"),
        required=False,
    )


alsoProvides(IFilingNumber, IFormFieldProvider)
