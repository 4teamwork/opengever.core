from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from datetime import datetime
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from opengever.document.checkout.handlers import create_initial_version
from zope.annotation import IAnnotations
from zope.interface import classProvides
from zope.interface import implements
import logging
import transaction


log = logging.getLogger('opengever.bundle.post_processing')
log.setLevel(logging.INFO)


INTERMEDIATE_COMMIT_INTERVAL = 200
VERSIONABLE_TYPES = ('opengever.document.document',)


class PostProcessingSection(object):
    """
    Section to perform post-processing steps that need to be done after
    the import is otherwise finished.

    Currently includes:

    - Creation of initial versions
      (which have been disabled during regular pipeline)
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.bundle = IAnnotations(transmogrifier)[BUNDLE_KEY]

    def __iter__(self):
        # Yield all items and collect them, so we can apply post-processing
        # steps *after* all the other sections have been executed
        items_to_post_process = []
        for item in self.previous:
            items_to_post_process.append(item)
            yield item

        # Any operations performed here will be applied after all the previous
        # sections have been run for all the items
        for count, item in enumerate(items_to_post_process, start=1):
            if item['_type'] in VERSIONABLE_TYPES:
                log.info("Creating initial version: %s" % item['_path'])
                create_initial_version(item['_object'])

            if count % INTERMEDIATE_COMMIT_INTERVAL == 0:
                self.commit_and_log(
                    "Intermediate commit during OGGBundle post-processing. "
                    "%s of %s items." % (count, len(items_to_post_process)))

        self.commit_and_log(
            "Final commit after OGGBundle post-processing. "
            "%s of %s items." % (count, len(items_to_post_process)))
        self.bundle.stats['timings']['done_post_processing'] = datetime.now()

    def commit_and_log(self, msg):
        transaction.get().note(msg)
        transaction.commit()
        log.info(msg)
