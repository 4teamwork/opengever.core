from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.document.checkout.handlers import create_initial_version
from zope.interface import classProvides
from zope.interface import implements
import logging


log = logging.getLogger('opengever.bundle.post_processing')
log.setLevel(logging.INFO)


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
        # Yield all items and collect them, so we can apply post-processing
        # steps *after* all the other sections have been executed
        items_to_post_process = []
        for item in self.previous:
            items_to_post_process.append(item)
            yield item

        # Any operations performed here will be applied after all the previous
        # sections have been run for all the items
        for item in items_to_post_process:
            log.info("Creating initial version: %s" % item['_path'])
            create_initial_version(item['_object'])
