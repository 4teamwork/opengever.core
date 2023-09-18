from collective.indexing.monkey import unpatch as unpatch_collective_indexing
from collective.transmogrifier.transmogrifier import Transmogrifier
from ftw.solr.interfaces import ISolrConnectionManager
from opengever.base.interfaces import INoSeparateConnectionForSequenceNumbers
from opengever.bundle.ldap import DisabledLDAP
from opengever.bundle.loader import GUID_INDEX_NAME
from opengever.bundle.sections.bundlesource import BUNDLE_INJECT_INITIAL_CONTENT_KEY
from opengever.bundle.sections.bundlesource import BUNDLE_KEY
from opengever.bundle.sections.bundlesource import BUNDLE_PATH_KEY
from opengever.bundle.sections.commit import INTERMEDIATE_COMMITS_KEY
from opengever.bundle.sections.map_principal_names_to_ids import CHECK_UNIQUE_PRINCIPALS_KEY
from opengever.bundle.sections.report import SKIP_REPORT_KEY
from plone import api
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.interface import alsoProvides
import logging


log = logging.getLogger('opengever.bundle')
log.setLevel(logging.INFO)


class BundleImporter(object):

    def __init__(self, site, bundle_path, disable_ldap=True,
                 create_guid_index=True, no_intermediate_commits=False,
                 possibly_unpatch_collective_indexing=True,
                 no_separate_connection_for_sequence_numbers=True,
                 skip_report=False, create_initial_content=False,
                 no_check_unique_principals=False):
        self.site = site
        self.bundle_path = bundle_path

        self.disable_ldap = disable_ldap
        self.create_guid_index = create_guid_index
        self.no_intermediate_commits = no_intermediate_commits
        self.possibly_unpatch_collective_indexing = possibly_unpatch_collective_indexing
        self.no_separate_connection_for_sequence_numbers = no_separate_connection_for_sequence_numbers
        self.skip_report = skip_report
        self.create_initial_content = create_initial_content
        self.no_check_unique_principals = no_check_unique_principals

    def run(self):
        log.info("Importing OGGBundle %s" % self.bundle_path)

        # Don't use a separate ZODB connection to issue sequence numbers in
        # order to avoid conflict errors during OGGBundle import
        if self.no_separate_connection_for_sequence_numbers:
            alsoProvides(self.site.REQUEST, INoSeparateConnectionForSequenceNumbers)

        # Add index to track imported GUIDs (if it doesn't exist yet)
        if self.create_guid_index:
            add_guid_index()

        transmogrifier = Transmogrifier(self.site)

        ann = IAnnotations(transmogrifier)
        ann[BUNDLE_PATH_KEY] = self.bundle_path
        ann[INTERMEDIATE_COMMITS_KEY] = not self.no_intermediate_commits
        ann[SKIP_REPORT_KEY] = self.skip_report
        ann[BUNDLE_INJECT_INITIAL_CONTENT_KEY] = self.create_initial_content
        ann[CHECK_UNIQUE_PRINCIPALS_KEY] = not self.no_check_unique_principals

        solr_enabled = api.portal.get_registry_record(
            'opengever.base.interfaces.ISearchSettings.use_solr',
            default=False)

        if solr_enabled:
            # Check if solr is running
            conn = getUtility(ISolrConnectionManager).connection
            if conn.get('/schema').status == -1:
                # XXX: The --skip-solr flag doesn't exist any more
                raise Exception(
                    "Solr isn't running, but solr reindexing is enabled. "
                    "Skipping solr reindexing via `--skip-solr`.")
        else:
            # TODO: In order to also allow this for TTW imports, we would
            # need to make sure to apply c.indexing patches again with
            # a context manager.
            if self.possibly_unpatch_collective_indexing:
                # Disable collective indexing as it can lead to too many
                # subtransactions
                unpatch_collective_indexing()

        if self.disable_ldap:
            with DisabledLDAP(self.site):
                transmogrifier(u'opengever.bundle.oggbundle')
        else:
            transmogrifier(u'opengever.bundle.oggbundle')

        bundle = IAnnotations(transmogrifier)[BUNDLE_KEY]
        timings = bundle.stats['timings']

        if 'migration_finished' in timings:
            duration = timings['migration_finished'] - timings['start_loading']
            log.info("Duration: %.2fs" % duration.total_seconds())


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
