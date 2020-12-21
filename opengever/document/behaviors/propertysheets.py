from plone.autoform.interfaces import IFormFieldProvider
from plone.schema import JSONField
from plone.supermodel import model
from zope.interface import alsoProvides


class IPropertySheets(model.Schema):

    property_sheets = JSONField(
        title=u'Property sheets with custom properties.',
        required=False
    )

    model.fieldset(
        u'properties',
        label=u'User defined property sheets.',
        fields=[
            u'property_sheets',
            ],
        )


alsoProvides(IPropertySheets, IFormFieldProvider)
