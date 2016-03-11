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

    def _build_docs_for_type(self, portal_type):
            type_dump_path = pjoin(
                self.schema_dumps_dir,
                '{}.json'.format(portal_type))
            try:
                type_dump = json.load(open(type_dump_path))
            except IOError:
                self._show_create_schema_dumps_message()
                raise

            field_docs = []
            for schema in type_dump['schemas']:

                for field in schema['fields']:
                    field_doc = self._build_docs_for_field(field)
                    field_docs.append(field_doc)

            type_template = env.get_template('type.rst')
            type_doc = type_template.render(
                dict(
                    portal_type=portal_type,
                    title=type_dump['title'],
                    field_docs=u'\n'.join(field_docs),
                )
            )

            return type_doc

    def _build_docs_for_field(self, field):
        field = field.copy()

        if not field['desc'].strip():
            field.pop('desc')

        if not field['required']:
            field.pop('required')

        if 'default' in field:
            default = field['default']
            if not self._is_placeholder(default):
                # Convert to JSON representation
                default = json.dumps(default)
            field['default'] = default

        if 'vocabulary' in field:
            vocab = field['vocabulary']
            if not self._is_placeholder(vocab):
                vocab = json.dumps(vocab)
            field['vocabulary'] = vocab

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
