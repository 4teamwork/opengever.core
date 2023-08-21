from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.bundle.loader import BundleLoader
from zope.annotation.interfaces import IAnnotations
from zope.interface import classProvides
from zope.interface import implements
import logging


logger = logging.getLogger('opengever.bundle.bundlesource')
logger.setLevel(logging.INFO)


BUNDLE_KEY = 'opengever.bundle.bundle'
BUNDLE_PATH_KEY = 'opengever.bundle.bundle_path'
BUNDLE_INGESTION_SETTINGS_KEY = 'opengever.bundle.ingestion_settings'
BUNDLE_INJECT_INITIAL_CONTENT_KEY = 'opengever.bundle.inject_initial_content'


class BundleSourceSection(object):
    """Injects items from an OGGBundle into the pipeline.
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.transmogrifier = transmogrifier

        annotations = IAnnotations(transmogrifier)

        bundle_path = annotations.get(BUNDLE_PATH_KEY)
        if not bundle_path:
            raise Exception(
                "No bundle_path specified. Please pass the bundle_path in "
                "annotations on the transmogrifier object, for example: "
                "IAnnotations(transmogrifier)[BUNDLE_PATH_KEY] = "
                "'/path/to/bundle'")

        ingestion_settings = annotations.get(BUNDLE_INGESTION_SETTINGS_KEY)

        inject_initial_content = annotations.get(BUNDLE_INJECT_INITIAL_CONTENT_KEY, False)
        self.bundle = BundleLoader(
            bundle_path,
            inject_initial_content=inject_initial_content
        ).load(ingestion_settings)
        annotations[BUNDLE_KEY] = self.bundle

    def __iter__(self):
        return iter(self.bundle)
