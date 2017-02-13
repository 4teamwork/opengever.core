from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.document.checkout.handlers import create_initial_version
from zope.interface import classProvides
from zope.interface import implements
import logging
import transaction


log = logging.getLogger('opengever.bundle.post_processing')
log.setLevel(logging.INFO)


INTERMEDIATE_COMMIT_INTERVAL = 1000


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

    def __iter__(self):
        self.commit_and_log("Committing transaction before post-processing.")
        log.info("Transaction committed.")

        # Yield all items and collect them, so we can apply post-processing
        # steps *after* all the other sections have been executed
        items_to_post_process = []
        for item in self.previous:
            items_to_post_process.append(item)
            yield item

        # Any operations performed here will be applied after all the previous
        # sections have been run for all the items
        for count, item in enumerate(items_to_post_process, start=1):
            log.info("Creating initial version: %s" % item['_path'])
            create_initial_version(item['_object'])

            if count % INTERMEDIATE_COMMIT_INTERVAL == 0:
                self.commit_and_log(
                    "Intermediate commit during OGGBundle post-processing. "
                    "%s of %s items." % (count, len(items_to_post_process)))

        self.commit_and_log(
            "Final commit after OGGBundle post-processing. "
            "%s of %s items." % (count, len(items_to_post_process)))

    def commit_and_log(self, msg):
        transaction.get().note(msg)
        log.info(msg)
        transaction.commit()
