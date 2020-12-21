from plone.supermodel import loadString


class PropertySheetSchemas(object):

    @classmethod
    def list(cls, context):
        for name in property_sheets:
            yield cls.get(name)

    @classmethod
    def get(cls, name):
        if name not in property_sheets:
            return None

        serialized_schema = property_sheets.get(name, None)
        model = loadString(serialized_schema, policy=u'propertysheets')
        schema_class = model.schemata[name]

        return schema_class


property_sheets = {
    "question": """
    <model xmlns:form="http://namespaces.plone.org/supermodel/form" xmlns:i18n="http://xml.zope.org/namespaces/i18n" xmlns:indexer="http://namespaces.plone.org/supermodel/indexer" xmlns:marshal="http://namespaces.plone.org/supermodel/marshal" xmlns:security="http://namespaces.plone.org/supermodel/security" xmlns="http://namespaces.plone.org/supermodel/schema">
      <schema name="question">
        <field name="bar" type="zope.schema.TextLine">
          <required>True</required>
          <title>bar</title>
        </field>
      </schema>
    </model>
    """
}
