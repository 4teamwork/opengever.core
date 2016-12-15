from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.bundle.loader import BundleLoader
from zope.annotation.interfaces import IAnnotations
from zope.interface import classProvides
from zope.interface import implements
import logging


logger = logging.getLogger('opengever.setup.jsonsource')
logger.setLevel(logging.INFO)


BUNDLE_PATH_KEY = 'opengever.setup.bundle_path'
JSON_STATS_KEY = 'opengever.setup.json_stats'


class JSONSourceSection(object):
    """Injects items from an OGGBundle into the pipeline.
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.transmogrifier = transmogrifier

        if hasattr(transmogrifier, 'bundle_path'):
            self.bundle_path = transmogrifier.bundle_path
        else:
            self.bundle_path = options.get('bundle_path')

        # Store the bundle path in global annotations on the
        # transmogrifier object for use by later sections
        IAnnotations(transmogrifier)[BUNDLE_PATH_KEY] = self.bundle_path

        IAnnotations(transmogrifier)[JSON_STATS_KEY] = {'errors': {}}

        self.bundle = BundleLoader(self.bundle_path)

    def __iter__(self):
        return iter(self.bundle)
