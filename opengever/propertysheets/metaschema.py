from opengever.propertysheets.definition import PropertySheetSchemaDefinition
from plone.supermodel import model
from zope import schema
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary


@provider(IContextSourceBinder)
def make_field_types_vocabulary(context):
    return SimpleVocabulary.fromValues(
        PropertySheetSchemaDefinition.FACTORIES.keys()
    )


class IFieldDefinition(model.Schema):

    name = schema.TextLine(required=True)
    field_type = schema.Choice(
        required=True, source=make_field_types_vocabulary
    )
    title = schema.TextLine(required=False)
    description = schema.TextLine(required=False)
    required = schema.Bool(required=False)
    values = schema.List(
        default=None,
        value_type=schema.TextLine(),
        required=False,
    )
