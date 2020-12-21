from plone.autoform.interfaces import IFormFieldProvider
from plone.schema import JSONField
from plone.supermodel import model
from z3c.form import validator
from zope.interface import alsoProvides
from zope.schema import getFieldsInOrder
from opengever.propertysheets.definition import PropertySheetSchemas


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


class PropertySheetsValidator(validator.SimpleFieldValidator):

    def validate(self, value):
        # use new document_type from request, or fallback to the one currently set
        if 'form.widgets.IDocumentMetadata.document_type' in self.request:
            document_type = self.request.get(
                'form.widgets.IDocumentMetadata.document_type')[0]
        else:
            document_type = self.context.document_type

        if not document_type:
            return

        schema_class = PropertySheetSchemas.get(document_type)
        if schema_class is None:
            return

        obj = value or {}

        sheet_for_type = obj.get(document_type, {})
        for name, field in getFieldsInOrder(schema_class):
            sheet_value = sheet_for_type.get(name, None)
            field.validate(sheet_value)


validator.WidgetValidatorDiscriminators(
    PropertySheetsValidator,
    field=IPropertySheets['property_sheets'],
    )
