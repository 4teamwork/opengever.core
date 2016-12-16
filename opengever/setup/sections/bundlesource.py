from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.bundle.loader import BundleLoader
from zope.annotation.interfaces import IAnnotations
from zope.interface import classProvides
from zope.interface import implements
import logging


logger = logging.getLogger('opengever.setup.bundlesource')
logger.setLevel(logging.INFO)


BUNDLE_KEY = 'opengever.setup.bundle'
BUNDLE_PATH_KEY = 'opengever.setup.bundle_path'
JSON_STATS_KEY = 'opengever.setup.json_stats'


class BundleSourceSection(object):
    """Injects items from an OGGBundle into the pipeline.
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.transmogrifier = transmogrifier

        IAnnotations(transmogrifier)[JSON_STATS_KEY] = {'errors': {}}

        bundle_path = IAnnotations(transmogrifier).get(BUNDLE_PATH_KEY)
        if not bundle_path:
            raise Exception(
                "No bundle_path specified. Please pass the bundle_path in "
                "annotations on the transmogrifier object, for example: "
                "IAnnotations(transmogrifier)[BUNDLE_PATH_KEY] = "
                "'/path/to/bundle'")

        self.bundle = BundleLoader(bundle_path)

        # Store a reference to the bundle for later sections to use
        IAnnotations(transmogrifier)[BUNDLE_KEY] = self.bundle

    def __iter__(self):
        return iter(self.bundle)
