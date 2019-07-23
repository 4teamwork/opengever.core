# Avoid import error for Products.Archetypes.BaseBTreeFolder
from Products.Archetypes import atapi  # noqa
from collective.indexing.monkey import unpatch as unpatch_collective_indexing
from collective.transmogrifier.transmogrifier import Transmogrifier
from ftw.solr.interfaces import ISolrConnectionManager
from opengever.base.interfaces import INoSeparateConnectionForSequenceNumbers
from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.bundle.ldap import DisabledLDAP
from opengever.bundle.loader import GUID_INDEX_NAME
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from opengever.bundle.sections.bundlesource import BUNDLE_PATH_KEY
from opengever.bundle.sections.commit import INTERMEDIATE_COMMITS_KEY
from opengever.core.debughelpers import get_first_plone_site
from opengever.core.debughelpers import setup_plone
from plone import api
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.interface import alsoProvides
import argparse
import logging
import sys
import transaction


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def parse_args(argv):
    parser = argparse.ArgumentParser(description='Import an OGGBundle')
    parser.add_argument('bundle_path',
                        help='Path to the .oggbundle directory')
    parser.add_argument('--no-intermediate-commits', action='store_true',
                        help="Don't to intermediate commits")

    args = parser.parse_args(argv)
    return args


def import_oggbundle(app, args):
    """Handler for the 'bin/instance import' zopectl command.
    """
    setup_logging()

    # Discard the first three arguments, because they're not "actual" arguments
    # but cruft that we get because of the way bin/instance [zopectl_cmd]
    # scripts work.
    args = parse_args(sys.argv[3:])

    log.info("Importing OGGBundle %s" % args.bundle_path)

    plone = setup_plone(get_first_plone_site(app))

    # mark request with GEVER layer
    alsoProvides(plone.REQUEST, IOpengeverBaseLayer)

    # Don't use a separate ZODB connection to issue sequence numbers in
    # order to avoid conflict errors during OGGBundle import
    alsoProvides(plone.REQUEST, INoSeparateConnectionForSequenceNumbers)

    # Add index to track imported GUIDs (if it doesn't exist yet)
    add_guid_index()

    transmogrifier = Transmogrifier(plone)

    ann = IAnnotations(transmogrifier)
    ann[BUNDLE_PATH_KEY] = args.bundle_path
    ann[INTERMEDIATE_COMMITS_KEY] = not args.no_intermediate_commits

    solr_enabled = api.portal.get_registry_record(
        'opengever.base.interfaces.ISearchSettings.use_solr',
        default=False)

    if solr_enabled:
        # Check if solr is running
        conn = getUtility(ISolrConnectionManager).connection
        if conn.get('/schema').status == -1:
            raise Exception(
                "Solr isn't running, but solr reindexing is enabled. "
                "Skipping solr reindexing via `--skip-solr`.")
    else:
        # Disable collective indexing as it can lead to too many
        # subtransactions
        unpatch_collective_indexing()

    with DisabledLDAP(plone):
        transmogrifier(u'opengever.bundle.oggbundle')

    bundle = IAnnotations(transmogrifier)[BUNDLE_KEY]
    timings = bundle.stats['timings']

    if 'migration_finished' in timings:
        duration = timings['migration_finished'] - timings['start_loading']
        log.info("Duration: %.2fs" % duration.total_seconds())

    log.info("Committing transaction...")
    transaction.get().note(
        "Finished import of OGGBundle %r" % args.bundle_path)
    transaction.commit()
    log.info("Done.")


def add_guid_index():
    """Adds a FieldIndex 'bundle_guid' if it doesn't exist yet.

    This index is only used by OGGBundle imports, and is used to track GUIDs
    of already imported objects and efficiently query them. This is necessary
    to enable partial / delta imports, and to accurately query the catalog to
    build reports about imported objects.

    This index will likely be removed after successful migrations, so code
    outside the bundle import MUST NOT rely on it being present.
    """
    catalog = api.portal.get_tool('portal_catalog')
    if GUID_INDEX_NAME not in catalog.indexes():
        log.info("Adding GUID index %r" % GUID_INDEX_NAME)
        catalog.addIndex(GUID_INDEX_NAME, 'FieldIndex')
    else:
        log.info("GUID index %r already exists" % GUID_INDEX_NAME)


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
