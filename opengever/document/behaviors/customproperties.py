from opengever.propertysheets.assignment import get_document_assignment_slots
from opengever.propertysheets.field import PropertySheetField
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope.interface import alsoProvides


class IDocumentCustomProperties(model.Schema):

    # XXX temporarily omit it from classic UI form rendering
    form.omitted('custom_properties')
    custom_properties = PropertySheetField(
        request_key='form.widgets.IDocumentMetadata.document_type',
        attribute_name='document_type',
        assignemnt_prefix='IDocumentMetadata.document_type',
        title=u'Property sheets with custom properties.',
        valid_assignment_slots_factory=get_document_assignment_slots,
        required=False,
    )

    model.fieldset(
        u'properties',
        label=u'Custom properties',
        fields=[
            u'custom_properties',
            ],
        )


alsoProvides(IDocumentCustomProperties, IFormFieldProvider)
