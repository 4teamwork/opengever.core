from plone.autoform.interfaces import IFormFieldProvider
from plone.schema import JSONField
from plone.supermodel import loadString
from plone.supermodel import model
from z3c.form import validator
from zope.interface import alsoProvides
from zope.schema import getFieldsInOrder


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

        # POC, use hardcoded additional schema
        if document_type != 'question':
            return

        obj = value or {}

        model = loadString(str_schema, policy=u'customfields')
        schema_class = model.schemata['opengever.custom1']
        schema_name = schema_class.getName()

        sheet_for_type = obj.get(document_type, {})

        for name, field in getFieldsInOrder(schema_class):
            sheet_value = sheet_for_type.get(name, None)
            field.validate(sheet_value)

        pass


validator.WidgetValidatorDiscriminators(
    PropertySheetsValidator,
    field=IPropertySheets['property_sheets'],
    )


str_schema = """
<model xmlns:form="http://namespaces.plone.org/supermodel/form" xmlns:i18n="http://xml.zope.org/namespaces/i18n" xmlns:indexer="http://namespaces.plone.org/supermodel/indexer" xmlns:marshal="http://namespaces.plone.org/supermodel/marshal" xmlns:security="http://namespaces.plone.org/supermodel/security" xmlns="http://namespaces.plone.org/supermodel/schema">
  <schema name="opengever.custom1">
    <field name="bar" type="zope.schema.TextLine">
      <required>True</required>
      <title>bar</title>
    </field>
  </schema>
</model>
"""

