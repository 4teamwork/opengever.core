from opengever.base.schema import Identifier
from opengever.base.schema import MultiTypeField
from opengever.propertysheets import _
from opengever.propertysheets.assignment import PropertySheetAssignmentVocabulary
from opengever.propertysheets.definition import isidentifier
from opengever.propertysheets.definition import PropertySheetSchemaDefinition
from opengever.propertysheets.exceptions import InvalidDefaultValue
from plone.supermodel import model
from zope import schema
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import invariant
from zope.interface import provider
from zope.schema import Choice
from zope.schema import Set
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
        description=_(u'help_name', default=u'Field name (alphanumeric, lowercase, '
                                            u'no special characters)'),
        required=True,
        max_length=32,
        pattern='^[a-z_0-9]*$',
        constraint=isidentifier,
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
        max_length=48,
    )
    description = schema.TextLine(
        title=_(u'label_description', default=u'Description'),
        description=_(u'help_description', default=u'Description'),
        required=False,
        max_length=128,
    )
    required = schema.Bool(
        title=_(u'label_required', default=u'Required'),
        description=_(u'help_required', default=u'Whether or not the field is required'),
        required=False,
    )
    default = MultiTypeField(
        title=_(u'label_default', default=u'Default'),
        description=_(u'help_default', default=u'Default value for this field'),
        required=False,
        allowed_types=[
            schema.TextLine,
            schema.Text,
            schema.Int,
            schema.Bool,
            schema.Date,
            schema.List,
            schema.Set,
        ],
    )
    values = schema.List(
        title=_(u'label_values', default=u'Allowed values'),
        description=_(u'help_values',
                      default=u'List of values that are allowed for this field (one per line)'),
        required=False,
        default=None,
        value_type=schema.TextLine(),
    )
    available_as_docproperty = schema.Bool(
        title=_(u'label_available_as_docproperty', default=u'Available as docproperty'),
        description=_(u'help_available_as_docproperty',
                      default=u'Whether the field should be available as docproperty or not'),
        required=False,
        default=False,
    )
    read_group = schema.TextLine(
        title=_(u'label_read_group', default=u'Read Group'),
        description=_(u'help_read_group',
                      default=u'If specified, only members of this group can read the field value.'),
        required=False,
    )
    write_group = schema.TextLine(
        title=_(u'label_write_group', default=u'Write Group'),
        description=_(u'help_write_group',
                      default=u'If specified, only members of this group can write the field value.'),
        required=False,
    )

    @invariant
    def valid_default_value(obj):
        data = obj.copy()

        # Prefill "soft-required" fields the same as the API endpoint would
        data.update({
            'title': data.get('title', u''),
            'description': data.get('description', u''),
            'required': data.get('required', False)
        })

        no_default_marker = object()
        default = data.pop('default', no_default_marker)
        if default is no_default_marker:
            return

        tmp_def = PropertySheetSchemaDefinition.create('tmp')
        tmp_def.add_field(**data)
        field = tmp_def.get_fields()[0][1]

        if isinstance(field, Set) and isinstance(field.value_type, Choice):
            # Multiple choice fields strictly require their default to be
            # of type 'set' (which can't be expressed in JSON). So if it's
            # a list, convert it. Otherwise, it's an invalid default anyway,
            # so we just let zope.schema handle it and raise WrongType.
            if isinstance(default, list):
                default = set(default)
        try:
            field.validate(default)
        except Exception:
            raise InvalidDefaultValue(default)


class IPropertySheetDefinition(model.Schema):

    id = Identifier(
        title=_(u'label_id', default=u'ID'),
        description=_(u'help_id', default=u'ID of this property sheet (alphanumeric, '
                                          u'lowercase, no special characters)'),
        required=False,
        max_length=32,
        pattern='^[a-z_0-9]*$',
        constraint=isidentifier,
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
