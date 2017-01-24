from collective.transmogrifier.transmogrifier import Transmogrifier
from opengever.bundle.sections.bundlesource import BUNDLE_PATH_KEY
from opengever.core.debughelpers import get_first_plone_site
from opengever.core.debughelpers import setup_plone
from zope.annotation import IAnnotations
import logging
import sys
import transaction


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def import_oggbundle(app, args):
    """Handler for the 'bin/instance import' zopectl command.
    """
    # Set Zope's default StreamHandler's level to INFO (default is WARNING)
    # to make sure output gets logged on console
    stream_handler = logging.root.handlers[0]
    stream_handler.setLevel(logging.INFO)

    bundle_path = sys.argv[3]
    log.info("Importing OGGBundle %s" % bundle_path)

    plone = setup_plone(get_first_plone_site(app))
    transmogrifier = Transmogrifier(plone)
    IAnnotations(transmogrifier)[BUNDLE_PATH_KEY] = bundle_path
    transmogrifier(u'opengever.bundle.oggbundle')

    log.info("Committing transaction...")
    transaction.commit()
    log.info("Done.")
