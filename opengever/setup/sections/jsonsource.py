from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultMatcher
from zope.interface import classProvides
from zope.interface import implements
import json
import logging
import os.path


logger = logging.getLogger('opengever.setup.jsonsource')


class JSONSourceSection(object):
    """Injects items from a JSON file into the pipeline."""

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.transmogrifier = transmogrifier

        self.key = defaultMatcher(options, 'key', name)
        self.json_dir = options.get('json_dir')
        self.filename = options.get('filename')

        self.portal_type = options.get('portal_type')

        self.filepath = os.path.join(self.json_dir, self.filename)

    def read_json_file(self):
        try:
            with open(self.filepath, "rb") as file_:
                return json.load(file_)
        except IOError:
            logger.info("Could not read file '{}'. Skipping...".format(
                self.filepath))
            return []

    def __iter__(self):
        for item in self.previous:
            yield item

        for item in self.read_json_file():
            item[u'_source'] = self.filename
            if self.portal_type:
                item[u'_type'] = self.portal_type
            yield item
