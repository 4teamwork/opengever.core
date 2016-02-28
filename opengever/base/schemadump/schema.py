from collections import OrderedDict
from five import grok
from opengever.base.schemadump.config import GEVER_TYPES
from opengever.base.schemadump.field import FieldDumper
from opengever.base.schemadump.helpers import DirectoryHelperMixin
from opengever.base.schemadump.helpers import join_lines
from opengever.base.schemadump.helpers import translate_de
from opengever.base.schemadump.log import setup_logging
from opengever.base.utils import pretty_json
from opengever.core.debughelpers import get_first_plone_site
from opengever.core.debughelpers import setup_plone
from os.path import join as pjoin
from plone import api
from plone.dexterity.utils import iterSchemataForType
from plone.supermodel.interfaces import FIELDSETS_KEY
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.schema import getFieldsInOrder
import os
import transaction


log = setup_logging(__name__)


class SchemaDumper(object):
    """Dumps a simple Python representation of a zope.schema Schema interface.
    """

    def dump(self, schema):
        log.info("  Dumping schema %r" % schema.__identifier__)

        fields = []
        field_dumper = FieldDumper(schema)

        for name, field in getFieldsInOrder(schema):
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
        fieldsets_for_schema = {}

        # Should probably use plone.autoform.utils.mergedTaggedValuesForIRO
        # fpr this instead, to merge tagged values across interfaces
        for fs in schema.queryTaggedValue(FIELDSETS_KEY, []):
            fieldsets_for_schema[fs.label] = fs.fields
        return fieldsets_for_schema


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


class JSONSchemaDumpWriter(DirectoryHelperMixin):
    """Dumps a JSON representation of common GEVER types and their schemas.
    """

    def dump_to_fs(self):
        result = join_lines(self._dump())
        return result

    def purge_schema_dumps(self):
        dir_ = self.schema_dumps_dir
        for name in os.listdir(dir_):
            if name.endswith('.json'):
                os.remove(pjoin(dir_, name))

    def _dump(self):
        type_dumper = TypeDumper()

        self.purge_schema_dumps()
        for portal_type in GEVER_TYPES:
            type_dump = type_dumper.dump(portal_type)
            dump_path = pjoin(self.schema_dumps_dir, '%s.json' % portal_type)

            with open(dump_path, 'w') as dump_file:
                json_dump = pretty_json(type_dump)
                dump_file.write(json_dump)

            log.info('Dumped: %s\n' % dump_path)
            yield json_dump


def dump_schemas():
    """Dump schemas of common GEVER content types to the filesystem.

    Dumps will be JSON representations of the schemas and their fields.
    """
    transaction.doom()
    writer = JSONSchemaDumpWriter()
    result = writer.dump_to_fs()
    return result


class DumpSchemasView(grok.View):
    """Helper view to dump schemas from a running instance.
    """

    grok.name('dump-schemas')
    grok.context(IPloneSiteRoot)
    grok.require('cmf.ManagePortal')

    def render(self):
        result = dump_schemas()
        return result


def dump_schemas_zopectl_handler(app, args):
    """Handler for the 'bin/instance dump_schemas' zopectl command.
    """
    setup_plone(get_first_plone_site(app))
    dump_schemas()
