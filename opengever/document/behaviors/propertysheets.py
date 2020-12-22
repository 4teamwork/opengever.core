from opengever.propertysheets.definition import PropertySheetSchemas
from plone.autoform.interfaces import IFormFieldProvider
from plone.schema import JSONField
from plone.supermodel import model
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.schema import getFieldsInOrder


class PropertySheetField(JSONField):

    def _validate(self, value):
        super(PropertySheetField, self)._validate(value)

        request = getRequest()

        if 'form.widgets.IDocumentMetadata.document_type' in request:
            document_type = request.get(
                'form.widgets.IDocumentMetadata.document_type')[0]
        elif self.context:
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


class IPropertySheets(model.Schema):

    property_sheets = PropertySheetField(
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
