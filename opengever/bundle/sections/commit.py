from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from zope.annotation import IAnnotations
from zope.interface import classProvides
from zope.interface import implements
import logging
import transaction


logger = logging.getLogger('opengever.bundle.commit')
logger.setLevel(logging.INFO)


INTERMEDIATE_COMMITS_KEY = 'intermediate_commits'


class CommitSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.every = int(options.get('every', 1000))
        self.previous = previous
        self.intermediate_commits = IAnnotations(transmogrifier).get(
            INTERMEDIATE_COMMITS_KEY)

    def __iter__(self):
        for count, item in enumerate(self.previous, start=1):
            if count % self.every == 0 and self.intermediate_commits:
                logger.info("Intermediate commit after %s items..." % count)
                transaction.commit()
                logger.info("Commit successful.")

            yield item

        logger.info("Commit after bundle import...")
        transaction.commit()
        logger.info("Commit successful.")
