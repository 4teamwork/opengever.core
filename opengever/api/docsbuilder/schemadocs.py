from jinja2 import Environment
from jinja2 import PackageLoader
from opengever.base.schemadump.config import GEVER_TYPES
from opengever.base.schemadump.helpers import DirectoryHelperMixin
from os.path import join as pjoin
import json
import os
import re


env = Environment(
    loader=PackageLoader('opengever.api.docsbuilder', 'templates'),
)

SCHEMA_DOC_EXTENSION = 'inc'


class SchemaDocsBuilder(DirectoryHelperMixin):
    """Builds ReStructuredText documents from JSON dumps of content types.
    """

    def build(self):
        self._purge_schema_docs()
        for portal_type in GEVER_TYPES:
            type_doc = self._build_docs_for_type(portal_type)

            # Don't use .rst as the extension so that the document doesn't
            # get included in the TOC multiple times
            doc_filename = '.'.join((portal_type, SCHEMA_DOC_EXTENSION))
            doc_path = pjoin(self.schema_docs_dir, doc_filename)

            with open(doc_path, 'w') as doc_file:
                doc_file.write(type_doc.encode('utf-8'))
            print "Updated {}".format(doc_path)

    def ordered_fields(self, schema):
        """Return (field_name, field_info) tuples in order according to
        the `field_order` property.
        """
        field_order = schema['field_order']

        def keyfunc(pair):
            key, value = pair
            try:
                idx = field_order.index(key)
            except ValueError:
                idx = -1
            return idx

        return sorted(schema['properties'].items(), key=keyfunc)

    def _build_docs_for_type(self, portal_type):
            schema_filename = '{}.schema.json'.format(portal_type)
            schema_path = pjoin(self.schema_dumps_dir, schema_filename)

            try:
                json_schema = json.load(open(schema_path))
            except IOError:
                self._show_create_schema_dumps_message()
                raise

            field_docs = []

            for field_name, field_info in self.ordered_fields(json_schema):
                required = field_name in json_schema.get('required', [])
                field_doc = self._build_docs_for_field(
                    field_name, field_info, required)
                field_docs.append(field_doc)

            type_template = env.get_template('type.rst')
            type_doc = type_template.render(
                dict(
                    portal_type=portal_type,
                    title=json_schema['title'],
                    field_docs=u'\n'.join(field_docs),
                )
            )

            return type_doc

    def _build_docs_for_field(self, field_name, field_info, required=False):
        field = field_info.copy()
        field['name'] = field_name
        field['type'] = field['_zope_schema_type']

        if not field['description'].strip():
            field.pop('description')

        if required:
            field['required'] = True

        if 'default' in field:
            default = field['default']
            if not self._is_placeholder(default):
                # Convert to JSON representation
                default = json.dumps(default)
            field['default'] = default

        if 'enum' in field:
            field['vocabulary'] = json.dumps(field['enum'])
        elif '_vocabulary' in field:
            # placeholder
            field['vocabulary'] = field['_vocabulary']

        self._cleanup_field_values(field)
        field_template = env.get_template('field.rst')
        field_doc = field_template.render(**field)
        return field_doc

    def _is_placeholder(self, value):
        stringish = isinstance(value, basestring)
        return stringish and re.match('<.*>', value)

    def _show_create_schema_dumps_message(self):
        msg = (
            "\n\033[0;31m"
            "Could not find expected schema dumps. "
            "Please create schema dumps first before building docs!\n"
            "Create schema dumps by either visiting the "
            "@@dump-schemas view on the site root or running \n\n"
            "bin/instance dump_schemas"
            "\033[0m\n"
        )
        print msg

    def _purge_schema_docs(self):
        dir_ = self.schema_docs_dir
        for name in os.listdir(dir_):
            if name.endswith('.' + SCHEMA_DOC_EXTENSION):
                os.remove(pjoin(dir_, name))

    def _cleanup_field_values(self, field):
        description = field.get('description')
        if description:
            # Fixes: https://github.com/4teamwork/opengever.core/issues/6340
            #
            # We need to use newline chars instead of <br> in schema
            # descriptions for new lines because the new UI does not render html
            # tags in field descriptions.
            #
            # Unfortunately, using a new-line char will unindent the description
            # block and will raise a sphinx build warning which will cause a
            # test failure.
            #
            # We remove the newline chars in the description fields completely
            # to fix the layout in the build documentation and to fix the tests.
            field['description'] = description.replace('\n', ' ')
