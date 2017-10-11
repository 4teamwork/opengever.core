from collective.transmogrifier.transmogrifier import Transmogrifier
from opengever.base.interfaces import INoSeparateConnectionForSequenceNumbers
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.bundle.ldap import DisabledLDAP
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from opengever.bundle.sections.bundlesource import BUNDLE_PATH_KEY
from opengever.core.debughelpers import get_first_plone_site
from opengever.core.debughelpers import setup_plone
from zope.annotation import IAnnotations
from zope.interface import alsoProvides
import logging
import sys
import transaction


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def import_oggbundle(app, args):
    """Handler for the 'bin/instance import' zopectl command.
    """
    setup_logging()
    bundle_path = sys.argv[3]
    log.info("Importing OGGBundle %s" % bundle_path)

    plone = setup_plone(get_first_plone_site(app))

    # mark request with GEVER layer
    alsoProvides(plone.REQUEST, IOpengeverBaseLayer)

    # Don't use a separate ZODB connection to issue sequence numbers in
    # order to avoid conflict errors during OGGBundle import
    alsoProvides(plone.REQUEST, INoSeparateConnectionForSequenceNumbers)

    transmogrifier = Transmogrifier(plone)
    IAnnotations(transmogrifier)[BUNDLE_PATH_KEY] = bundle_path

    with DisabledLDAP(plone):
        transmogrifier(u'opengever.bundle.oggbundle')

    bundle = IAnnotations(transmogrifier)[BUNDLE_KEY]
    timings = bundle.stats['timings']

    if 'migration_finished' in timings:
        duration = timings['migration_finished'] - timings['start_loading']
        log.info("Duration: %.2fs" % duration.total_seconds())

    log.info("Committing transaction...")
    transaction.get().note("Finished import of OGGBundle %r" % bundle_path)
    transaction.commit()
    log.info("Done.")


def setup_logging():
    # Set Zope's default StreamHandler's level to INFO (default is WARNING)
    # to make sure output gets logged on console
    stream_handler = logging.root.handlers[0]
    stream_handler.setLevel(logging.INFO)

    # Also write logs to a dedicated migration log in the working directory.
    file_handler = logging.FileHandler('migration.log')
    file_handler.setFormatter(stream_handler.formatter)
    file_handler.setLevel(logging.INFO)
    logging.root.addHandler(file_handler)
