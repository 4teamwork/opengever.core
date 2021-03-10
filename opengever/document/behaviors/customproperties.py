from opengever.document import _
from opengever.propertysheets.assignment import get_document_assignment_slots
from opengever.propertysheets.assignment import DOCUMENT_DEFAULT_ASSIGNMENT_SLOT
from opengever.propertysheets.field import PropertySheetField
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope.interface import alsoProvides


class IDocumentCustomProperties(model.Schema):

    custom_properties = PropertySheetField(
        request_key='form.widgets.IDocumentMetadata.document_type',
        attribute_name='document_type',
        assignemnt_prefix='IDocumentMetadata.document_type',
        valid_assignment_slots_factory=get_document_assignment_slots,
        default_slot=DOCUMENT_DEFAULT_ASSIGNMENT_SLOT,
    )

    model.fieldset(
        u'custom_properties',
        label=_(u'Custom properties'),
        fields=[
            u'custom_properties',
            ],
        )


alsoProvides(IDocumentCustomProperties, IFormFieldProvider)
