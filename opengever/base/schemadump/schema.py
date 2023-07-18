from collections import OrderedDict
from opengever.base.behaviors.translated_title import TRANSLATED_TITLE_NAMES
from opengever.base.schemadump.config import ALLOWED_REVIEW_STATES
from opengever.base.schemadump.config import DEFAULT_MANAGEABLE_ROLES
from opengever.base.schemadump.config import GEVER_SQL_TYPES
from opengever.base.schemadump.config import GEVER_SQL_TYPES_TO_OGGBUNDLE_TYPES
from opengever.base.schemadump.config import GEVER_TYPES
from opengever.base.schemadump.config import GEVER_TYPES_TO_OGGBUNDLE_TYPES
from opengever.base.schemadump.config import IGNORED_FIELDS
from opengever.base.schemadump.config import IGNORED_OGGBUNDLE_FIELDS
from opengever.base.schemadump.config import JSON_SCHEMA_FIELD_TYPES
from opengever.base.schemadump.config import MANAGEABLE_ROLES_BY_TYPE
from opengever.base.schemadump.config import PARENTABLE_TYPES
from opengever.base.schemadump.config import ROOT_TYPES
from opengever.base.schemadump.config import SEQUENCE_NUMBER_LABELS
from opengever.base.schemadump.field import FieldDumper
from opengever.base.schemadump.field import SQLFieldDumper
from opengever.base.schemadump.helpers import DirectoryHelperMixin
from opengever.base.schemadump.helpers import mkdir_p
from opengever.base.schemadump.helpers import translate_de
from opengever.base.schemadump.json_schema_helper import JSONSchema
from opengever.journal.form import IManualJournalEntry
from os.path import join as pjoin
from pkg_resources import resource_filename
from plone import api
from plone.dexterity.utils import iterSchemataForType
from plone.supermodel.interfaces import FIELDSETS_KEY
from sqlalchemy.ext.declarative.base import _is_mapped_class
from zope.dottedname.resolve import resolve as resolve_dotted
from zope.schema import getFieldsInOrder
import logging
import transaction


log = logging.getLogger(__name__)


class SchemaDumper(object):
    """Dumps a simple Python representation of a zope.schema Schema interface.
    """

    def dump(self, schema):
        log.info("  Dumping schema %r" % schema.__identifier__)

        fields = []
        field_dumper = FieldDumper(schema)

        for name, field in getFieldsInOrder(schema):
            dottedname = '.'.join((schema.__identifier__, field.getName()))
            if dottedname in IGNORED_FIELDS:
                log.info("  Skipping field %s" % dottedname)
                continue

            field_dump = field_dumper.dump(field)
            fields.append(field_dump)

        schema_dump = OrderedDict((
            ('name', schema.__identifier__),
            ('fields', fields),
        ))

        # Fieldsets
        fieldsets = self._get_fieldsets_for_schema(schema)
        if fieldsets:
            schema_dump['fieldsets'] = fieldsets

        return schema_dump

    def _get_fieldsets_for_schema(self, schema):
        fieldsets_for_schema = OrderedDict()

        # Should probably use plone.autoform.utils.mergedTaggedValuesForIRO
        # fpr this instead, to merge tagged values across interfaces
        for fs in schema.queryTaggedValue(FIELDSETS_KEY, []):
            fieldsets_for_schema[fs.label] = fs.fields
        return fieldsets_for_schema


class SQLSchemaDumper(object):
    """Dumps a simple Python representation of a SQLAlchemy mapped class.
    """

    def dump(self, klass):
        log.info("  Dumping SQL schema %r" % klass.__name__)

        fields = []
        field_dumper = SQLFieldDumper(klass)

        tbl = klass.__table__
        for column in tbl.columns:
            if column.foreign_keys:
                # XXX: Skip ForeignKeys for now, because it's unclear how
                # exactly they should be handled.
                continue
            field_dump = field_dumper.dump(column)
            fields.append(field_dump)

        schema_dump = OrderedDict((
            ('name', klass.__name__),
            ('fields', fields),
        ))

        return schema_dump


class TypeDumper(object):
    """Dumps a simple Python representation of an FTI and its schemas.
    """

    def dump(self, portal_type):
        log.info("Dumping schemas for portal_type %r" % portal_type)
        fti = self._get_fti(portal_type)
        type_title = translate_de(fti.title, domain=fti.i18n_domain)

        schemas = []
        schema_dumper = SchemaDumper()

        for schema in iterSchemataForType(portal_type):
            schema_dump = schema_dumper.dump(schema)
            schemas.append(schema_dump)

        type_dump = OrderedDict((
            ('portal_type', portal_type),
            ('title', type_title),
            ('schemas', schemas),
        ))

        return type_dump

    def _get_fti(self, portal_type):
        types_tool = api.portal.get_tool('portal_types')
        return types_tool[portal_type]


class SQLTypeDumper(object):
    """Dumps a simple Python representation of SQLAlchemy mapped type.
    """

    def dump(self, sql_type):
        log.info("Dumping schemas for SQL type%r" % sql_type)
        # SQL type names are prefixed with an underscore to distinguish
        # them from actual portal_types
        dottedname = sql_type.lstrip('_')
        main_klass = resolve_dotted(dottedname)

        schemas = []
        schema_dumper = SQLSchemaDumper()

        # Also consider columns from base classes (inheritance).
        # We only consider one level of inheritance though, we don't look
        # up base classes recursively.
        bases = list(filter(_is_mapped_class, main_klass.__bases__))
        mapper_args = getattr(main_klass, '__mapper_args__', {})

        if bases and 'polymorphic_identity' not in mapper_args:
            raise NotImplementedError(
                "Unexpected inheritance for %r: Mapped base classes, but "
                "no polymorphic_identity found!" % main_klass)

        for base_class in bases:
            if list(filter(_is_mapped_class, base_class.__bases__)) != []:
                raise NotImplementedError(
                    "More than one level of inheritance currently not"
                    "supported when dumping SQL schemas.")

        for cls in [main_klass] + bases:
            schema = schema_dumper.dump(cls)
            schemas.append(schema)

        type_dump = OrderedDict((
            ('portal_type', sql_type),
            ('title', main_klass.__name__),
            ('schemas', schemas),
        ))

        return type_dump


class JSONSchemaBuilder(object):
    """Builds a JSON Schema representation of a single Schema.
    """

    def __init__(self, schema):
        self.schema = schema

    def build_schema(self, additional_properties=False):
        schema_dump = SchemaDumper().dump(self.schema)

        self.schema = JSONSchema(
            title=schema_dump['name'],
            additional_properties=additional_properties,
        )

        for field in schema_dump['fields']:
            prop_def = self._property_definition_from_field(field)
            self.schema.add_property(field['name'], prop_def)

        return self.schema

    def _property_definition_from_field(self, field):
        """Create a JSON Schema property definition from a field info dump.
        """
        prop_def = self._js_type_from_zope_type(field['type'])

        prop_def['title'] = field['title']
        prop_def['description'] = field['description']
        prop_def['_zope_schema_type'] = field['type']

        self._process_choice(prop_def, field)
        self._process_max_length(prop_def, field)
        self._process_default(prop_def, field)
        self._process_vocabulary(prop_def, field)
        self._process_required(prop_def, field)

        return prop_def

    def _js_type_from_zope_type(self, zope_type):
        """Map a zope.schema type to a JSON schema (JavaScript) type.

        Returns a minimal property definition dict including at least a
        'type', and possibly a 'format' as well.
        """
        if zope_type not in JSON_SCHEMA_FIELD_TYPES:
            raise Exception(
                "Don't know what JS type to map %r to. Please map it in "
                "JSON_SCHEMA_FIELD_TYPES first." % zope_type)

        type_spec = JSON_SCHEMA_FIELD_TYPES[zope_type].copy()
        return type_spec

    def _process_choice(self, prop_def, field):
        if field['type'] == 'Choice':
            prop_def['type'] = field['value_type']

    def _process_max_length(self, prop_def, field):
        if field.get('max_length') is not None:
            prop_def['maxLength'] = field['max_length']

    def _process_default(self, prop_def, field):
        if 'default' in field:
            prop_def['default'] = field['default']

    def _process_vocabulary(self, prop_def, field):
        if field.get('vocabulary'):
            vocab = field['vocabulary']
            if isinstance(vocab, basestring) and vocab.startswith('<'):
                # Placeholder vocabulary (like <Any valid user> )
                prop_def['_vocabulary'] = vocab
            else:
                prop_def['enum'] = vocab

    def _process_required(self, prop_def, field):
        if field.get('required', False):
            if field['name'] not in TRANSLATED_TITLE_NAMES:
                self.schema.set_required(field['name'])


class PortalTypeJSONSchemaBuilder(JSONSchemaBuilder):
    """Builds a JSON Schema representation of a single GEVER type.
    """

    def __init__(self, portal_type):
        self.portal_type = portal_type
        self.schema = None

        if portal_type in GEVER_TYPES:
            self.type_dumper = TypeDumper()
        elif portal_type in GEVER_SQL_TYPES:
            self.type_dumper = SQLTypeDumper()
        else:
            raise Exception("Unmapped type: %r" % portal_type)

    def build_schema(self):
        type_dump = self.type_dumper.dump(self.portal_type)

        self.schema = JSONSchema(
            title=type_dump['title'],
            additional_properties=False,
        )
        field_order = []
        # Collect field info from all schemas (base schema + behaviors)
        for _schema in type_dump['schemas']:
            # Note: This is not the final / "correct" field order as displayed
            # in the user interface (which should eventually honor fieldsets
            # and plone.autoform directives).
            # The intent here is rather to keep a *consistent* order for now.
            field_order.extend([field['name'] for field in _schema['fields']])

            translated_title_fields = []
            for field in _schema['fields']:
                prop_def = self._property_definition_from_field(field)
                self.schema.add_property(field['name'], prop_def)

                if field['name'] in TRANSLATED_TITLE_NAMES:
                    translated_title_fields.append(field['name'])

            if translated_title_fields:
                self.schema.require_any_of(translated_title_fields)

        self.schema.set_field_order(field_order)
        return self.schema


class OGGBundleJSONSchemaBuilder(object):
    """Builds a JSON Schema representation of a single OGGBundle type.
    """

    def __init__(self, portal_type):
        self.portal_type = portal_type
        self.short_name = GEVER_TYPES_TO_OGGBUNDLE_TYPES[portal_type]

        # Bundle schema (array of items)
        self.schema = None
        # Content type schema (item, i.e. GEVER type)
        self.ct_schema = None

    def build_schema(self):
        # The OGGBundle JSON schemas all are flat arrays of items, where the
        # actual items' schemas are (more or less) the GEVER content types'
        # schemas, stored in #/definitions/<short_name>
        self.schema = JSONSchema(type_='array')
        self.schema._schema['items'] = {
            "$ref": "#/definitions/%s" % self.short_name}

        # Build the standard content type schema
        self.ct_schema = PortalTypeJSONSchemaBuilder(self.portal_type).build_schema()

        # Tweak the content type schema for use in OGGBundles
        self._add_review_state_property()
        self._add_creator_property()
        self._add_guid_properties()
        self._add_participation_property()
        self._add_journal_property()
        self._add_permissions_property()
        self._add_file_properties()
        self._add_sequence_number_property()
        self._add_old_path_property()
        self._add_mail_properties()

        self._filter_fields()
        self.ct_schema.make_optional_properties_nullable()

        # Finally add the CT schema under #/definitions/<short_name>
        self.schema.add_definition(self.short_name, self.ct_schema)
        return self.schema

    def _add_review_state_property(self):
        # XXX: Eventually, these states should be dynamically generated by
        # interrogating the FTI / workflow tool. Hardcoded for now.
        self.ct_schema.add_property(
            'review_state',
            {'type': 'string',
             'enum': ALLOWED_REVIEW_STATES[self.portal_type]},
            required=True,
        )

    def _add_creator_property(self):
        self.ct_schema.add_property(
            '_creator',
            {'type': 'string'},
            required=False,
        )

    def _add_guid_properties(self, with_parent_reference=True):
        self.ct_schema.add_property('guid', {'type': 'string'}, required=True)

        if self.portal_type not in ROOT_TYPES:
            # Everything except repository roots or workspace roots
            # supports a parent_guid or a parent_reference.
            self.ct_schema.add_property('parent_guid', {'type': 'string'})
            if not with_parent_reference:
                return

            array_of_ints = {
                "type": "array",
                "items": {"type": "integer"},
            }
            self.ct_schema.add_property(
                'parent_reference', {'type': 'array', 'items': array_of_ints})

            if self.portal_type not in PARENTABLE_TYPES:
                # Parent pointers are optional for parentable types. For any
                # other non-root types, they're required
                self.ct_schema.require_any_of(['parent_guid', 'parent_reference'])

    def _add_permissions_property(self):
        if not self.portal_type == 'opengever.document.document':
            permissions_schema = self._build_permission_subschema()
            self.ct_schema._schema['properties']['_permissions'] = {
                "$ref": "#/definitions/permission"}

            # XXX: This is just to preserve order in definitions for now
            self.schema._schema['definitions'] = OrderedDict()
            self.schema._schema['definitions'][self.short_name] = None

            self.schema.add_definition('permission', permissions_schema)

    def _add_participation_property(self):
        if self.portal_type == 'opengever.dossier.businesscasedossier':
            self.ct_schema.add_property('_participations', {
                'type': 'array',
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "participant_id": {
                            "type": "string"
                        },
                        "roles": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        }
                    }
                }
            })

    def _add_journal_property(self):
        if self.portal_type == 'opengever.dossier.businesscasedossier':
            subschema = JSONSchemaBuilder(IManualJournalEntry).build_schema().serialize()
            subschema.pop('$schema')
            subschema["properties"]["time"] = {"type": ["null", "string"],
                                               "format": "datetime",
                                               "_zope_schema_type": "Datetime"}
            self.ct_schema.add_property('_journal_entries', {
                'type': 'array',
                "items": subschema
            })

    def _build_permission_subschema(self):
        subschema = JSONSchema(additional_properties=False)
        string_array = {
            "type": "array",
            "items": {"type": "string"},
        }

        subschema.add_property('block_inheritance', {"type": "boolean"})

        manageable_roles = MANAGEABLE_ROLES_BY_TYPE.get(
            self.portal_type, DEFAULT_MANAGEABLE_ROLES)

        for role_name in manageable_roles:
            subschema.add_property(role_name, string_array)

        return subschema

    def _add_file_properties(self):
        if self.portal_type == 'opengever.document.document':
            self.ct_schema.add_property('filepath', {'type': 'string'})

            # In OGGBundles we always require a title for documents
            self.ct_schema.set_required('title')

            # XXX: Documents without files? For now we always require filepath
            self.ct_schema.set_required('filepath')

    def _add_sequence_number_property(self):
        if self.portal_type not in SEQUENCE_NUMBER_LABELS:
            return

        desc = SEQUENCE_NUMBER_LABELS[self.portal_type]
        self.ct_schema.add_property('sequence_number', {
            'type': 'integer',
            'title': u'Laufnummer',
            'description': desc,
        })

    def _add_old_path_property(self):
        self.ct_schema.add_property('_old_paths', {
            'type': 'array',
            'title': u'Earlier path',
        })

    def _add_mail_properties(self):
        # Mails in OGGBundles are expecter in documents.json, and for large
        # parts treated like documents. Only later (bundle loader) will their
        # *actual* portal_type (ftw.mail.mail) be determined and set.
        if self.portal_type == 'opengever.document.document':
            self.ct_schema.add_property('original_message_path',
                                        {'type': 'string'})

    def _filter_fields(self):
        filtered_fields = IGNORED_OGGBUNDLE_FIELDS.get(self.short_name, [])
        for field_name in filtered_fields:
            self.ct_schema.drop_property(field_name)


class OGGBundleJSONSchemaSQLBuilder(OGGBundleJSONSchemaBuilder):
    """Builds a JSON Schema representation of a single OGGBundle SQL type.
    """

    def __init__(self, portal_type):
        self.portal_type = portal_type
        self.short_name = GEVER_SQL_TYPES_TO_OGGBUNDLE_TYPES[portal_type]

        # Bundle schema (array of items)
        self.schema = None
        # Content type schema (item, i.e. GEVER type)
        self.ct_schema = None

    def build_schema(self):
        # The OGGBundle JSON schemas all are flat arrays of items, where the
        # actual items' schemas are (more or less) the GEVER content types'
        # schemas, stored in #/definitions/<short_name>
        self.schema = JSONSchema(type_='array')
        self.schema._schema['items'] = {
            "$ref": "#/definitions/%s" % self.short_name}

        # Build the standard content type schema
        self.ct_schema = PortalTypeJSONSchemaBuilder(self.portal_type).build_schema()

        # Tweak the content type schema for use in OGGBundles
        self._add_guid_properties(with_parent_reference=False)
        self._filter_fields()
        self.ct_schema.make_optional_properties_nullable()

        # Finally add the CT schema under #/definitions/<short_name>
        self.schema.add_definition(self.short_name, self.ct_schema)
        return self.schema


class JSONSchemaDumpWriter(DirectoryHelperMixin):
    """Collects JSON Schema representations of common GEVER types and dumps
    them to the file system.
    """

    def dump(self):
        for filename, schema in build_all_gever_schemas():
            dump_path = pjoin(self.schema_dumps_dir, filename)
            schema.dump(dump_path)


class OGGBundleJSONSchemaDumpWriter(DirectoryHelperMixin):
    """Collects JSON Schema representations of OGGBundle types and dumps
    them to the file system.
    """

    def dump(self):
        dump_dir = pjoin(resource_filename('opengever.bundle', 'schemas/'))
        mkdir_p(dump_dir)

        for filename, schema in build_all_bundle_schemas():
            dump_path = pjoin(dump_dir, filename)
            schema.dump(dump_path)


def build_all_gever_schemas():
    """Collects JSON Schema representations of common GEVER types.
    """
    for portal_type in GEVER_TYPES + GEVER_SQL_TYPES:
        builder = PortalTypeJSONSchemaBuilder(portal_type)
        schema = builder.build_schema()
        filename = '%s.schema.json' % portal_type
        yield filename, schema


def build_all_bundle_schemas():
    """Collects JSON Schema representations of OGGBundle types.
    """
    for portal_type, short_name in GEVER_TYPES_TO_OGGBUNDLE_TYPES.items():
        builder = OGGBundleJSONSchemaBuilder(portal_type)
        schema = builder.build_schema()
        filename = '%ss.schema.json' % short_name
        yield filename, schema

    for portal_type, short_name in GEVER_SQL_TYPES_TO_OGGBUNDLE_TYPES.items():
        builder = OGGBundleJSONSchemaSQLBuilder(portal_type)
        schema = builder.build_schema()
        filename = '%ss.schema.json' % short_name
        yield filename, schema


def dump_schemas():
    """Dump JSON Schemas of common GEVER content types to the filesystem.

    Dumps will be JSON Schema representations of the schemas and their fields.
    """
    transaction.doom()
    writer = JSONSchemaDumpWriter()
    result = writer.dump()
    return result


def dump_oggbundle_schemas():
    """Dump JSON Schemas for the OGGBundle exchange format to the filesystem.
    """
    transaction.doom()
    writer = OGGBundleJSONSchemaDumpWriter()
    result = writer.dump()
    return result
