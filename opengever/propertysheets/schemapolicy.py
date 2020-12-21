from zope.interface import implementer
from plone.supermodel.parser import ISchemaPolicy


@implementer(ISchemaPolicy)
class PropertySheetsSchemaPolicy(object):

    def module(self, schemaName, tree):
        return 'opengever.propertysheets.generated'

    def bases(self, schemaName, tree):
        return ()

    def name(self, schemaName, tree):
        return schemaName
