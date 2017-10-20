from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from zope.annotation.interfaces import IAnnotations
from zope.interface import classProvides
from zope.interface import implements
import logging
import os
import subprocess


logger = logging.getLogger('opengever.bundle.progress')
logger.setLevel(logging.INFO)


def get_rss():
    """Get current memory usage (RSS) of this process.
    """
    out = subprocess.check_output(
        ["ps", "-p", "%s" % os.getpid(), "-o", "rss"])
    try:
        return int(out.splitlines()[-1].strip())
    except ValueError:
        return 0


class ProgressSection(object):
    """Reports progress count
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.bundle = IAnnotations(transmogrifier)[BUNDLE_KEY]
        self.interval = int(options.get('interval', 100))
        self.count = 0
        self.total = sum(self.bundle.stats['bundle_counts_raw'].values())

    def __iter__(self):
        logger.info(
            "Starting migration (%s raw items total in bundle)" % self.total)

        for item in self.previous:
            self.count += 1

            if self.count % self.interval == 0:
                percentage = 100 * float(self.count) / float(self.total)
                logger.info("%s of %s items (%.2f%%) processed." % (
                    self.count, self.total, percentage))

                rss = get_rss() / 1024.0
                logger.info("Current memory usage (RSS): %0.2f MB" % rss)
            yield item

        logger.info("Done. Processed %s items total." % self.count)
