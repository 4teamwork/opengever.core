from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossier
from opengever.propertysheets.assignment import DOSSIER_DEFAULT_ASSIGNMENT_SLOT
from opengever.propertysheets.assignment import get_dossier_assignment_slots
from opengever.propertysheets.field import PropertySheetField
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope.interface import alsoProvides


class IDossierCustomProperties(model.Schema):

    custom_properties = PropertySheetField(
        request_key='form.widgets.IDossier.dossier_type',
        attribute_name='dossier_type',
        schema_interface=IDossier,
        assignemnt_prefix='IDossier.dossier_type',
        valid_assignment_slots_factory=get_dossier_assignment_slots,
        default_slot=DOSSIER_DEFAULT_ASSIGNMENT_SLOT,
    )

    model.fieldset(
        u'custom_properties',
        label=_(u'Custom properties'),
        fields=[
            u'custom_properties',
        ],
    )


alsoProvides(IDossierCustomProperties, IFormFieldProvider)
