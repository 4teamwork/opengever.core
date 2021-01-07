from opengever.propertysheets.storage import PropertySheetSchemaStorage
from plone.autoform.interfaces import IFormFieldProvider
from plone.schema import IJSONField
from plone.schema import JSONField
from plone.supermodel import model
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.schema import getFieldsInOrder


class IPropertySheetField(IJSONField):
    pass


@implementer(IPropertySheetField)
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

        assignment = 'IDocumentMetadata.document_type.{}'.format(document_type)
        schema_definition = PropertySheetSchemaStorage().query(assignment)
        if schema_definition is None:
            return

        obj = value or {}

        sheet_for_type = obj.get(document_type, {})
        for name, field in getFieldsInOrder(schema_definition.schema_class):
            sheet_value = sheet_for_type.get(name, None)
            field.validate(sheet_value)


class ICustomProperties(model.Schema):

    custom_properties = PropertySheetField(
        title=u'Property sheets with custom properties.',
        required=False
    )

    model.fieldset(
        u'properties',
        label=u'User defined property sheets.',
        fields=[
            u'custom_properties',
            ],
        )


alsoProvides(ICustomProperties, IFormFieldProvider)
