from ftw.dictstorage.sql import DictStorageModel
from ftw.testing.layer import ComponentRegistryIsolationLayer
from glob2 import glob
from opengever.base import model
from opengever.base.model import create_session
from opengever.base.utils import pretty_json
from opengever.core.solr_testing import SolrReplicationAPIClient
from path import Path
from plone.app.testing import PloneFixture
from plone.testing import zca
from plone.testing.z2 import Startup
from sqlalchemy import text
from types import NoneType
from ZODB.blob import copyTransactionsFromTo
from ZODB.DB import DB
from ZODB.FileStorage.FileStorage import FileStorage
from zope.component.hooks import getSite
import json
import os
import re
import shutil
import transaction


CACHE_ENABLED = (os.environ.get('GEVER_CACHE_TEST_DB', '')
                 .lower().strip() == 'true')
CACHE_VERBOSE = (os.environ.get('GEVER_CACHE_VERBOSE', '')
                 .lower().strip() == 'true')
BUILDOUT_DIR = Path(__file__).joinpath('..', '..', '..').abspath()


_CACHE_PLONE_SETUP = {
    'id': 'plone_setup',
    'description': 'Inludes the Plone setup (PloneFixture).',
    # When the bin/test file changes, we could end up with a new Plone.
    # This will cause the cache key to invalidate.
    'cache_globs': ('bin/test',),
    'has_sql': False,
    'has_solr': False,
}

_CACHE_GEVER_INSTALLATION = {
    'id': 'GEVER_installation',
    'description': 'Cache the installation of opengever and dependencies.',
    'cache_globs': ('opengever/core/profiles/**/*',
                    'opengever/testing/profiles/**/*',
                    'opengever/**/hooks.py',
                    'opengever/core/*test*',
                    'src/**/profiles/**/*',
                    'src/**/hooks.py',
                    'src/**/setuphandlers.py'),
    'exclude_cache_globs': ('**/*.pyc',),
    'extends': 'plone_setup',
}

_CACHE_GEVER_FIXTURE = {
    'id': 'GEVER_fixture',
    'description': 'Cache the fixture of opengever.core',
    'cache_globs': ('opengever/testing/**/*',),
    'exclude_cache_globs': ('**/*.pyc',
                            'opengever/testing/pages/**/*',),
    'extends': 'GEVER_installation',
}


STACK_DEFINITIONS = {
    'plone_setup': _CACHE_PLONE_SETUP,
    'GEVER_installation': _CACHE_GEVER_INSTALLATION,
    'GEVER_fixture': _CACHE_GEVER_FIXTURE,
}


class Stack(object):
    """An instance of a cache stack.

    Each DBCacheManager with a distinct `cache_label` will manage its own set
    of Stack instances. These are initialized using the stack definitions as
    a template, but after that are instances that are tied to their respective
    DBCacheManager.
    """

    def __init__(self, stackdef, cache_label):
        self.stack_id = stackdef['id']
        self.cache_label = cache_label

        self.description = stackdef['description']
        self.cache_globs = stackdef['cache_globs']
        self.exclude_cache_globs = stackdef.get('exclude_cache_globs', ())
        self.has_sql = stackdef.get('has_sql', True)
        self.has_solr = stackdef.get('has_solr', True)
        self.extends = stackdef.get('extends', None)

        self.path = None
        self.cachekey = None
        self.loaded = False

    def __repr__(self):
        return '<%s(cache_label=%r, stack_id=%r)>' % (
            self.__class__.__name__, self.cache_label, self.stack_id)


class DBCacheManager(object):
    """The DBCacheManager is used for speeding up single bin/test runs
    by caching the databases (zodb and sql) over multiple bin/test processes.

    The cache works by dumping the database into files in var/test-db-caches/
    and loading from this files on startup.

    The tricky part is the invalidation of the cache.
    This is done by invalidating when certain files have changed according to
    the modification time.
    All files need to be tracked which directly affect persistent data,
    such as generic setup profiles or builders.

    The cache manager works with multiple stacked database dumps.
    Those stacks make snapshots on multiple places while setting up the testing
    databases. They may invalidate individually.

    Caches can be entirely separated by giving them distinct cache labels.
    Each DBCacheManager with a different `cache_label` will dump to and load
    from its own var/test-db-caches/<cache_label> directory, and therefore will
    be isolated from other, incompatible caches.
    """

    top_stack_id = 'GEVER_fixture'

    def __init__(self, cache_label):
        self.cache_label = cache_label
        self.caches_dir = BUILDOUT_DIR.joinpath('var/test-db-caches/%s' % self.cache_label)
        self.cache_stacks = tuple(self._build_cache_stacks())
        self.data = {'site_site_manager_bases': {}}
        self._sql_deferred_load_stack = None
        self._solr_deferred_load_stack = None

    def load_from_cache(self):
        """Load the most-top stack which has a valid cache key.
        """
        if not CACHE_ENABLED:
            return None

        stack = self._find_cache_to_load()
        if stack is None:
            return None

        print '(Loading database cache stack {!r}) '.format(stack.stack_id),
        zodbDB = self._load_zodb_from(stack)
        self._load_data_from(stack)
        # Defer sql and solr loading: the sql database engine and Solr
        # connection are not configured yet at this point since the
        # opengever.core ZCML is not yet loaded.
        self._sql_deferred_load_stack = stack
        self._solr_deferred_load_stack = stack

        # Mark the loaded stack and it's parents as loaded.
        for stack_or_parent in self.chain_of(stack):
            stack_or_parent.loaded = True

        return zodbDB

    def contains(self, stack_id):
        return stack_id in self._stacks_by_id

    def stack_by_id(self, stack_id):
        return self._stacks_by_id[stack_id]

    def is_loaded_from_cache(self, stack_id):
        """Return ``True`` when the given stack has been loaded from cache.
        """
        assert self.contains(stack_id), 'Invalid stack.'
        stack = self.stack_by_id(stack_id)
        return stack.loaded

    def dump_to_cache(self, zodbDB, stack_id):
        """Dump the current databases to the cache, representing a given stack.
        """
        if not CACHE_ENABLED:
            return

        assert self.contains(stack_id), 'Invalid stack.'
        if self.is_loaded_from_cache(stack_id):
            # Don't dump to a stack which we've loaded from, or it will cause
            # quite a mess.
            return

        stack = self.stack_by_id(stack_id)
        print '(Dumping database cache stack {!r}) '.format(stack_id),
        stack.path.rmtree_p()
        stack.path.makedirs_p()
        self._dump_zodb_to(zodbDB, stack)
        self._dump_data_to(stack)
        self._dump_sql(stack)
        self._dump_solr(stack)
        self._dump_cachekey(stack)

    def apply_cache_fixes(self, stack_id):
        """Apply fixes for a specific cache stack.
        This is the place to restore non-persistent links between the database
        and volatile in-memory structures.
        """
        if not self.is_loaded_from_cache(stack_id):
            return

        stack = self.stack_by_id(stack_id)
        self._restore_site_site_manager_bases(stack)

        # We need to defer loading of SQL and Solr: at the time we load
        # the databases we have not loaded the GEVER ZCML and therefore
        # the SQL engine and/or Solr aren't yet configured.
        # Therefore loading the SQL and Solr is deferred until we fix the
        # first stack which supports them.

        if self._solr_deferred_load_stack and stack.has_solr:
            self._load_solr(self._solr_deferred_load_stack)
            self._solr_deferred_load_stack = None

        if self._sql_deferred_load_stack and stack.has_sql:
            self._load_sql(self._sql_deferred_load_stack)
            self._sql_deferred_load_stack = None

    def chain_of(self, stack):
        """All stacks extended by the given stack.
        """
        return self.cache_stacks[self.cache_stacks.index(stack):]

    def _build_cache_stacks(self):
        """Generate the cache stacks top-down.
        """
        self._stacks_by_id = {}

        stack = Stack(STACK_DEFINITIONS[self.top_stack_id], cache_label=self.cache_label)
        while stack:
            stack.path = self.caches_dir.joinpath(stack.stack_id)

            if self.cache_label != 'solr':
                # Only the Solr layer should attempt to dump/load Solr
                stack.has_solr = False

            assert stack.cachekey is None
            stack.cachekey = self._build_cachekey_from_globs(stack)

            self._stacks_by_id[stack.stack_id] = stack
            yield stack

            # Resolve extends into next stack, or terminate
            stackdef = STACK_DEFINITIONS.get(stack.extends)
            stack = None
            if stackdef:
                stack = Stack(stackdef, cache_label=self.cache_label)

    def _build_cachekey_from_globs(self, stack):
        """Build a cache from all files in the configured globs.
        We use the glob2 package because python's glob does not support
        recursive globbing (simlar to ``globstar``).
        """
        assert isinstance(stack.cache_globs, (list, tuple))

        exclude_paths = []
        for pattern in stack.exclude_cache_globs:
            exclude_paths.extend(map(Path, glob(BUILDOUT_DIR / pattern)))

        cachekey = {}
        for pattern in stack.cache_globs:
            for path in map(Path, glob(BUILDOUT_DIR / pattern)):
                if not path.isfile():
                    continue
                if path in exclude_paths:
                    continue
                cachekey[str(path)] = path.getmtime()

        return cachekey

    def _find_cache_to_load(self):
        """Find the top valid cache to load.
        """
        for stack in self.cache_stacks:
            if self._is_stack_valid_to_load(stack):
                return stack
        return None

    def _is_stack_valid_to_load(self, stack, verbose=CACHE_VERBOSE):
        """A cache is valid when
        - the cache exists
        - the parent cache is valid, when there is one
        - the cachekey did not change
        """
        if not stack.path.isdir():
            return False

        if stack.extends and \
           not self._is_stack_valid_to_load(self.stack_by_id(stack.extends), verbose=False):
            return False

        previous_cachekey = self._load_cachekey(stack)
        if verbose and stack.cachekey != previous_cachekey:
            print ''
            print '-' * 40
            print 'Cachekey changes in', stack.stack_id

            for path in sorted(set(stack.cachekey) | set(previous_cachekey)):
                if stack.cachekey.get(path) != previous_cachekey.get(path):
                    print '-', Path(path).relpath(BUILDOUT_DIR)

            print '-' * 40

        return stack.cachekey == previous_cachekey

    def _dump_zodb_to(self, zodbDB, stack):
        """Dump the zodbDB into a data.fs by constructing a FileStorage database
        and copying the transactions from the DemoStorage.
        """
        ori_site_manager_bases = None
        if getSite():
            # The __bases__ of our local persistent component registry is
            # probably a volatile site manager. Pickling it will corrupt the
            # database.
            # Therefore we remember the stack bases and remove the __bases__
            # for the duration of the DB dump.
            ori_site_manager_bases = getSite().getSiteManager().__bases__
            self.data['site_site_manager_bases'][str(stack.path.name)] = [
                base.__name__ for base in ori_site_manager_bases
            ]
            getSite().getSiteManager().__bases__ = ()

        transaction.commit()  # Make sure we have the latest state.
        # The transaction records in testing have no _extension set, causing
        # a RuntimeError when copied to a filestorage.
        map(lambda record: setattr(record, '_extension', record.extension),
            zodbDB.storage.iterator())

        zodb_file = str(stack.path.joinpath('zodb.fs'))
        blob_dir = str(stack.path.joinpath('blobs'))
        cache_storage = FileStorage(zodb_file, create=True,
                                    blob_dir=blob_dir)
        copyTransactionsFromTo(zodbDB.storage, cache_storage)

        if ori_site_manager_bases is not None:
            # Restore the __bases__ of the local persistent component registry,
            # which've removed above.
            getSite().getSiteManager().__bases__ = ori_site_manager_bases
            transaction.commit()

    def _load_zodb_from(self, stack):
        """Load the ZODB from the FileStorage cache.
        This does not copy the transactions back to the DemoStorage, because
        this will be hard to do because of missing features in the DemoStorage.
        The FileStorage is directly used as base for the later created
        DemoStorage instead.
        """
        zodb_file = str(stack.path.joinpath('zodb.fs'))
        blob_dir = str(stack.path.joinpath('blobs'))
        return DB(FileStorage(zodb_file, read_only=True,
                              blob_dir=blob_dir))

    def _restore_site_site_manager_bases(self, stack):
        """The __bases__ of the local persistent site manager are not dumped
        into the FileStorage cache, since they may be volatile, non-persistent.
        This method restores the site manager after loading from cache.
        This cannot happen at load-time though, since loading is done very
        early in the testing setup process, where the component registry bases
        we must base on are not yet set up.
        """
        bases_names = self.data['site_site_manager_bases'].get(
            str(stack.path.name))
        if not bases_names:
            return

        registries = map(zca.loadRegistry, bases_names)
        getSite().getSiteManager().__bases__ = registries

    def _dump_sql(self, stack):
        """Dumping the SQL is done by writing all sql statements from
        SQLAlchemy's iterdump to a sql dump file.
        """
        if not stack.has_sql:
            return

        sql_file = stack.path.joinpath('dump.sql')
        session = create_session()
        statements = session.connection().connection.connection.iterdump()
        sql_file.write_lines(statements, encoding='utf-8')

    def _load_sql(self, stack):
        """Loading the SQL is done by executing the the statements from the
        sql dump file.
        """
        if not stack.has_sql:
            return

        self._ensure_sql_database_is_empty()
        sql_file = stack.path.joinpath('dump.sql')
        sql_statements = ['DROP TABLE IF EXISTS opengever_upgrade_version']
        sql_statements.extend(re.split(r';\n', sql_file.bytes().decode('utf-8')))
        session = create_session()
        map(session.execute, map(text, sql_statements))
        transaction.commit()

    def _dump_solr(self, stack):
        """Dumping Solr is done by triggering a backup via Solr's replication
        API, and then moving away that backup (from Solr's data directory into
        the stack's cache directory).
        """
        if not stack.has_solr:
            return

        client = SolrReplicationAPIClient.get_instance()
        if not client._configured:
            raise Exception(
                "SolrReplicationAPIClient is unexpectedly not configured, "
                "even though stack is marked with 'has_solr=True'. "
                "Check your caching setup!")

        snapshot_name = 'solr-cache-%s' % stack.stack_id
        client.create_backup(snapshot_name)
        client.await_backuped()

        snapshot_filename = 'snapshot.bak-%s' % snapshot_name
        snapshot_src_path = client.data_dir().joinpath(snapshot_filename)
        cached_snapshot_path = stack.path.joinpath(snapshot_filename)

        print "Moving Solr snapshot %s to cache %s" % (snapshot_src_path, cached_snapshot_path)
        shutil.move(snapshot_src_path, cached_snapshot_path)

    def _load_solr(self, stack):
        """Loading Solr is done by copying back the Solr snapshot from the
        cache directory into Solr's data directory, and restoring it using
        Solr's replication API.
        """
        if not stack.has_solr:
            return

        client = SolrReplicationAPIClient.get_instance()
        if not client._configured:
            raise Exception(
                "SolrReplicationAPIClient is unexpectedly not configured, "
                "even though stack is marked with 'has_solr=True'. "
                "Check your caching setup!")

        snapshot_name = 'solr-cache-%s' % stack.stack_id
        snapshot_filename = 'snapshot.bak-%s' % snapshot_name

        cached_snapshot_path = stack.path.joinpath(snapshot_filename)
        snapshot_dst_path = client.data_dir().joinpath(snapshot_filename)

        print "Restoring Solr snapshot from cache %s to %s" % (cached_snapshot_path, snapshot_dst_path)
        snapshot_dst_path.rmtree_p()
        shutil.copytree(cached_snapshot_path, snapshot_dst_path)

        client.restore_backup(snapshot_name)
        client.await_restored()

    def _ensure_sql_database_is_empty(self):
        """In order to load a sql database from cache we need an empty databse.
        """
        session = create_session()
        for metadata_model in (model.Base.metadata,
                               DictStorageModel.metadata):
            metadata_model.drop_all(session.bind)

    def _dump_data_to(self, stack):
        """Dump any additional data to the stack.
        """
        data_file = stack.path.joinpath('data.json')
        data_file.write_bytes(json_dumps(self.data).decode('utf-8'))

    def _load_data_from(self, stack):
        """Load any additional data from the stack.
        """
        data_file = stack.path.joinpath('data.json')
        self.data = json_loads(data_file.bytes())

    def _dump_cachekey(self, stack):
        """Dump the cachekey for a stack.
        """
        cachekey_file = stack.path.joinpath('cachekey.json')
        cachekey_file.write_bytes(json_dumps(stack.cachekey).decode('utf-8'))

    def _load_cachekey(self, stack):
        """Load the cachekey for a stack.
        """
        cachekey_file = stack.path.joinpath('cachekey.json')
        return json_loads(cachekey_file.bytes())


# We set up two different DBCacheManagers here in order to isolate their caches.
#
# The ContentFixtureWithSolrLayer also sets up a GEVER fixture, but also needs
# to dump and load the Solr database. On the other hand, the regular
# ContentFixtureLayer MUST NOT attempt to dump / load Solr.
#
# All this indirection below is therefore needed to separate caches for the
# regular ContentFixtureLayer and the ContentFixtureWithSolrLayer by
# having them use their own DBCacheManagers, distinguished by their cache_label.

DB_CACHE_MANAGERS = {
    'default': DBCacheManager(cache_label='default'),
    'solr': DBCacheManager(cache_label='solr')
}


class CachedStartup(Startup):

    def __init__(self, *args, **kwargs):
        self.cache_label = kwargs.pop('cache_label')
        super(CachedStartup, self).__init__(*args, **kwargs)
        self['db_cache_manager'] = DB_CACHE_MANAGERS[self.cache_label]

    def setUpDatabase(self):
        zodbDB = self['db_cache_manager'].load_from_cache()
        if zodbDB is not None:
            # The db manager was able to load a zodb from a cache.
            # By setting it in self['zodbDB'], the database (stack) created
            # in the supercall will base on our cached filestorage database
            # and we have all cached data ready.
            self['zodbDB'] = zodbDB

        super(CachedStartup, self).setUpDatabase()

    def tearDownBasicProducts(self):
        """The products cannot be torn down: we probably operate on a cached
        read-only filestorage database.
        Therefore this method is overriden in order to not unistall products
        but still fix the Five globals.
        """

        # It's possible for Five's _register_monkies and _meta_type_regs
        # global variables to contain duplicates. This causes an unecessary
        # error in the LayerCleanup layer's tear-down. Guard against that
        # here

        try:
            from OFS import metaconfigure
        except ImportError:
            # Zope <= 2.12
            from Products.Five import fiveconfigure as metaconfigure
        metaconfigure._register_monkies = list(
            set(metaconfigure._register_monkies))
        metaconfigure._meta_type_regs = list(
            set(metaconfigure._meta_type_regs))


CACHED_STARTUP_DEFAULT = CachedStartup(
    cache_label='default',
    name='CACHED_STARTUP_DEFAULT')

CACHED_STARTUP_SOLR = CachedStartup(
    cache_label='solr',
    name='CACHED_STARTUP_SOLR')


class CachedPloneFixture(PloneFixture):

    defaultBases = (CACHED_STARTUP_DEFAULT, )

    def setUp(self):
        super(CachedPloneFixture, self).setUp()
        self['db_cache_manager'].dump_to_cache(self['zodbDB'], 'plone_setup')

    def setUpDefaultContent(self, app):
        if not self['db_cache_manager'].is_loaded_from_cache('plone_setup'):
            super(CachedPloneFixture, self).setUpDefaultContent(app)
        else:
            self['db_cache_manager'].apply_cache_fixes('plone_setup')

    def tearDownProducts(self, app):
        """Tear down products should not be necessary:
        we are trashing the database and isolating the z3 component registry.
        """


CACHED_PLONE_FIXTURE_DEFAULT = CachedPloneFixture(
    bases=(CACHED_STARTUP_DEFAULT, ),
    name='CACHED_PLONE_FIXTURE_DEFAULT')

CACHED_PLONE_FIXTURE_SOLR = CachedPloneFixture(
    bases=(CACHED_STARTUP_SOLR, ),
    name='CACHED_PLONE_FIXTURE_SOLR')

CACHED_COMPONENT_REGISTRY_ISOLATION = ComponentRegistryIsolationLayer(
    bases=(CACHED_PLONE_FIXTURE_DEFAULT, ),
    name='CACHED_COMPONENT_REGISTRY_ISOLATION')

CACHED_COMPONENT_REGISTRY_ISOLATION_SOLR = ComponentRegistryIsolationLayer(
    bases=(CACHED_PLONE_FIXTURE_SOLR,),
    name='CACHED_COMPONENT_REGISTRY_ISOLATION_SOLR')


def json_dumps(data):
    """Dump a data structure as json string while adding information about
    the setring type (unicode, binary).
    """
    def prepare(thing):
        if isinstance(thing, unicode):
            return u'u:{}'.format(thing)
        if isinstance(thing, str):
            return u'b:{}'.format(thing.decode('utf-8'))
        elif isinstance(thing, (int, long, float, bool, NoneType)):
            return thing
        elif isinstance(thing, (list, tuple)):
            return map(prepare, thing)
        elif isinstance(thing, dict):
            return dict(map(lambda pair: map(prepare, pair), thing.items()))
        else:
            raise TypeError('Not supported: {!r} ({!r})'.format(
                thing, type(thing)))
    return pretty_json(prepare(data))


def json_loads(data):
    """Load a string into a python data structure, while respecting string
    typing info added by the corresponding json_dumps function.
    """
    def prepare(thing):
        if isinstance(thing, unicode) and thing.startswith(u'u:'):
            return thing[2:]
        if isinstance(thing, unicode) and thing.startswith(u'b:'):
            return thing[2:].encode('utf-8')
        elif isinstance(thing, unicode):
            raise ValueError('No "u:" or "b:" prefixes: {!}'.format(thing))
        elif isinstance(thing, (int, long, float, bool, NoneType)):
            return thing
        elif isinstance(thing, list):
            return map(prepare, thing)
        elif isinstance(thing, dict):
            return dict(map(lambda pair: map(prepare, pair), thing.items()))
        else:
            raise TypeError('Not supported: {!r} ({!r})'.format(
                thing, type(thing)))
    return prepare(json.loads(data))
