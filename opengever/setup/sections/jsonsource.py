from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultMatcher
from jsonschema import FormatChecker
from jsonschema import validate
from opengever.base.schemadump import config
from opengever.base.schemadump.schema import OGGBundleJSONSchemaBuilder
from zope.interface import classProvides
from zope.interface import implements
import codecs
import json
import logging
import os.path
from zope.annotation.interfaces import IAnnotations


logger = logging.getLogger('opengever.setup.jsonsource')
logger.setLevel(logging.INFO)


BUNDLE_PATH_KEY = 'opengever.setup.bundle_path'
JSON_STATS_KEY = 'opengever.setup.json_stats'


class JSONSourceSection(object):
    """Injects items from a JSON file into the pipeline.

    If a portal_type is specified, also sets the _type for all items.

    If a jsonschema is registered for the portal_type also validates the
    file content against the schema.

    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.transmogrifier = transmogrifier

        self.key = defaultMatcher(options, 'key', name)
        self.filename = options.get('filename')
        if hasattr(transmogrifier, 'bundle_path'):
            self.bundle_path = transmogrifier.bundle_path
        else:
            self.bundle_path = options.get('bundle_path')

        if not os.path.exists(self.bundle_path):
            raise Exception("Bundle %s not found" % self.bundle_path)

        # Store the bundle path in global annotations on the
        # transmogrifier object for use by later sections
        IAnnotations(transmogrifier)[BUNDLE_PATH_KEY] = self.bundle_path

        IAnnotations(transmogrifier)[JSON_STATS_KEY] = {'errors': {}}

        self.portal_type = options.get('portal_type')
        self.json_schema = self.get_content_type_json_schema()

        self.filepath = os.path.join(self.bundle_path, self.filename)

    def get_content_type_json_schema(self):
        if not self.portal_type:
            return None
        if self.portal_type not in config.GEVER_TYPES:
            return None

        builder = OGGBundleJSONSchemaBuilder()
        return builder.build_schema(self.portal_type)

    def read_json_file(self):
        try:
            with codecs.open(self.filepath, 'r', 'utf-8-sig') as file_:
                return json.load(file_)
        except IOError:
            logger.info("Could not read file '{}'. Skipping...".format(
                self.filepath))
            return []

    def validate(self, data):
        if not self.json_schema:
            return

        validate(data, self.json_schema, format_checker=FormatChecker())

    def get_data(self):
        data = self.read_json_file()
        self.validate(data)
        return data

    def __iter__(self):
        logger.info('Yielding items from %s' % self.filename)
        for item in self.previous:
            yield item

        for item in self.get_data():
            item[u'_source'] = self.filename
            if self.portal_type:
                item[u'_type'] = self.portal_type
            yield item
