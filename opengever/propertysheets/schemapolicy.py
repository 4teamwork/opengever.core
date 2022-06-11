from plone.supermodel.parser import ISchemaPolicy
from zope.interface import implementer


@implementer(ISchemaPolicy)
class PropertySheetSchemaPolicy(object):
    """Custom schema policy for property sheet schemas.

    Currently used to inject a fake module name to easily identify property
    sheet schemas.
    """
    def module(self, schemaName, tree):
        return 'opengever.propertysheets.generated'

    def bases(self, schemaName, tree):
        return ()

    def name(self, schemaName, tree):
        return schemaName
