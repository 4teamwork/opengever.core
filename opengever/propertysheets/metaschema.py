from opengever.base.schema import Identifier
from opengever.propertysheets import _
from opengever.propertysheets.assignment import PropertySheetAssignmentVocabulary
from opengever.propertysheets.definition import PropertySheetSchemaDefinition
from plone.supermodel import model
from zope import schema
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@provider(IContextSourceBinder)
def make_propertysheet_assignment_vocabulary(context):
    return PropertySheetAssignmentVocabulary()(context)


@provider(IContextSourceBinder)
def make_field_types_vocabulary(context):
    vocab = SimpleVocabulary(
        [SimpleTerm(k, k, translate(v.title, context=getRequest()))
         for k, v in PropertySheetSchemaDefinition.FACTORIES.items()])
    return vocab


class IFieldDefinition(model.Schema):

    name = Identifier(
        title=_(u'label_name', default=u'Name'),
        description=_(u'help_name', default=u'Field name (alphanumeric, lowercase)'),
        required=True,
        pattern='^[a-z_0-9]*$',
    )
    field_type = schema.Choice(
        title=_(u'label_field_type', default=u'Field type'),
        description=_(u'help_field_type', default=u'Data type of this field'),
        required=True,
        source=make_field_types_vocabulary,
    )
    title = schema.TextLine(
        title=_(u'label_title', default=u'Title'),
        description=_(u'help_title', default=u'Title'),
        required=False,
    )
    description = schema.TextLine(
        title=_(u'label_description', default=u'Description'),
        description=_(u'help_description', default=u'Description'),
        required=False,
    )
    required = schema.Bool(
        title=_(u'label_required', default=u'Required'),
        description=_(u'help_required', default=u'Whether or not the field is required'),
        required=False,
    )
    values = schema.List(
        title=_(u'label_values', default=u'Allowed values'),
        description=_(u'help_values',
                      default=u'List of values that are allowed for this field'),
        required=False,
        default=None,
        value_type=schema.TextLine(),
    )


class IPropertySheetDefinition(model.Schema):

    id = Identifier(
        title=_(u'label_id', default=u'ID'),
        description=_(u'help_id', default=u'ID of this property sheet'),
        required=False,
        pattern='^[a-z_0-9]*$',
    )
    fields = schema.List(
        title=_(u'label_fields', default=u'Fields'),
        description=_(u'help_fields', default=u'Fields'),
        required=True,
        value_type=schema.Object(schema=IFieldDefinition),
    )
    assignments = schema.List(
        title=_(u'label_assignments', default=u'Assignments'),
        description=_(u'help_assignments',
                      default=u'What type of content this property sheet '
                              u'will be available for'),
        required=False,
        value_type=schema.Choice(
            source=make_propertysheet_assignment_vocabulary,
        ),
    )
