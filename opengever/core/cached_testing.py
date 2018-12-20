from ftw.dictstorage.sql import DictStorageModel
from ftw.testing.layer import ComponentRegistryIsolationLayer
from glob2 import glob
from opengever.base import model
from opengever.base.model import create_session
from opengever.base.utils import pretty_json
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
import transaction


CACHE_ENABLED = (os.environ.get('GEVER_CACHE_TEST_DB', '')
                 .lower().strip() == 'true')
CACHE_VERBOSE = (os.environ.get('GEVER_CACHE_VERBOSE', '')
                 .lower().strip() == 'true')
BUILDOUT_DIR = Path(__file__).joinpath('..', '..', '..').abspath()


CACHE_PLONE_SETUP = {
    'id': 'plone_setup',
    'description': 'Inludes the Plone setup (PloneFixture).',
    # When the bin/test file changes, we could end up with a new Plone.
    # This will cause the cache key to invalidate.
    'cache_globs': ('bin/test',),
    'has_sql': False,
}

CACHE_GEVER_INSTALLATION = {
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
    'extends': CACHE_PLONE_SETUP,
}

CACHE_GEVER_FIXTURE = {
    'id': 'GEVER_fixture',
    'description': 'Cache the fixture of opengever.core',
    'cache_globs': ('opengever/testing/**/*',),
    'exclude_cache_globs': ('**/*.pyc',
                            'opengever/testing/pages/**/*',),
    'extends': CACHE_GEVER_INSTALLATION,
}


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
    """

    top_stack = CACHE_GEVER_FIXTURE

    def __init__(self):
        self.caches_dir = BUILDOUT_DIR.joinpath('var/test-db-caches')
        self.cache_stacks = tuple(self._build_cache_stacks())
        self.data = {'site_site_manager_bases': {}}
        self._sql_deferred_load_stack = None

    def load_from_cache(self):
        """Load the most-top stack which has a valid cache key.
        """
        if not CACHE_ENABLED:
            return None

        stack = self._find_cache_to_load()
        if stack is None:
            return None

        print '(Loading database cache stack {!r}) '.format(stack['id']),
        zodbDB = self._load_zodb_from(stack)
        self._load_data_from(stack)
        # Defer sql loading: the sql database engine is not configured at this
        # point since the opengever.core ZCML is not yet loaded.
        self._sql_deferred_load_stack = stack

        # Mark the loaded stack and it's parents as loaded.
        for stack_or_parent in self.chain_of(stack):
            stack_or_parent['loaded'] = True

        return zodbDB

    def is_loaded_from_cache(self, stack):
        """Return ``True`` when the given stack has been loaded from cache.
        """
        assert stack in self.cache_stacks, 'Invalid stack.'
        return stack.get('loaded', False)

    def dump_to_cache(self, zodbDB, stack):
        """Dump the current databases to the cache, representing a given stack.
        """
        if not CACHE_ENABLED:
            return

        assert stack in self.cache_stacks, 'Invalid stack.'
        if self.is_loaded_from_cache(stack):
            # Don't dump to a stack which we've loaded from, or it will cause
            # quite a mess.
            return

        print '(Dumping database cache stack {!r}) '.format(stack['id']),
        stack['path'].rmtree_p()
        stack['path'].makedirs_p()
        self._dump_zodb_to(zodbDB, stack)
        self._dump_data_to(stack)
        self._dump_sql(stack)
        self._dump_cachekey(stack)

    def apply_cache_fixes(self, stack):
        """Apply fixes for a specific cache stack.
        This is the place to restore non-persistent links between the database
        and volatile in-memory structures.
        """
        if not self.is_loaded_from_cache(stack):
            return

        self._restore_site_site_manager_bases(stack)
        if self._sql_deferred_load_stack and stack.get('has_sql', True):
            # We need to defer loading of the sql: at the time we load
            # the databases we have not loaded the GEVER ZCML and therefore
            # the sql engine is not yet configured.
            # Therefore loading the SQL is deferred until we fix the first
            # stack which supports SQL.
            self._load_sql(self._sql_deferred_load_stack)
            self._sql_deferred_load_stack = None

    def chain_of(self, stack):
        """All stacks extended by the given stack.
        """
        return self.cache_stacks[self.cache_stacks.index(stack):]

    def _build_cache_stacks(self):
        """Generate the cache stacks top-down.
        """
        stack = self.top_stack
        while stack:
            stack['path'] = self.caches_dir.joinpath(stack['id'])
            assert stack.get('cachekey', None) is None
            stack['cachekey'] = self._build_cachekey_from_globs(stack)
            stack.setdefault('has_sql', True)
            yield stack
            stack = stack.get('extends')

    def _build_cachekey_from_globs(self, stack):
        """Build a cache from all files in the configured globs.
        We use the glob2 package because python's glob does not support
        recursive globbing (simlar to ``globstar``).
        """
        assert isinstance(stack['cache_globs'], (list, tuple))

        exclude_paths = []
        for pattern in stack.get('exclude_cache_globs', ()):
            exclude_paths.extend(map(Path, glob(BUILDOUT_DIR / pattern)))

        cachekey = {}
        for pattern in stack['cache_globs']:
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
        if not stack['path'].isdir():
            return False

        if stack.get('extends') and \
           not self._is_stack_valid_to_load(stack['extends'], verbose=False):
            return False

        previous_cachekey = self._load_cachekey(stack)
        if verbose and stack['cachekey'] != previous_cachekey:
            print ''
            print '-' * 40
            print 'Cachekey changes in', stack['id']

            for path in sorted(set(stack['cachekey']) | set(previous_cachekey)):
                if stack['cachekey'].get(path) != previous_cachekey.get(path):
                    print '-', Path(path).relpath(BUILDOUT_DIR)

            print '-' * 40

        return stack['cachekey'] == previous_cachekey

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
            self.data['site_site_manager_bases'][str(stack['path'].name)] = [
                base.__name__ for base in ori_site_manager_bases
            ]
            getSite().getSiteManager().__bases__ = ()

        transaction.commit()  # Make sure we have the latest state.
        # The transaction records in testing have no _extension set, causing
        # a RuntimeError when copied to a filestorage.
        map(lambda record: setattr(record, '_extension', record.extension),
            zodbDB.storage.iterator())

        zodb_file = str(stack['path'].joinpath('zodb.fs'))
        blob_dir = str(stack['path'].joinpath('blobs'))
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
        zodb_file = str(stack['path'].joinpath('zodb.fs'))
        blob_dir = str(stack['path'].joinpath('blobs'))
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
            str(stack['path'].name))
        if not bases_names:
            return

        registries = map(zca.loadRegistry, bases_names)
        getSite().getSiteManager().__bases__ = registries

    def _dump_sql(self, stack):
        """Dumping the SQL is done by writing all sql statements from
        SQLAlchemy's iterdump to a sql dump file.
        """
        if not stack.get('has_sql', True):
            return

        sql_file = stack['path'].joinpath('dump.sql')
        session = create_session()
        statements = session.connection().connection.connection.iterdump()
        sql_file.write_lines(statements, encoding='utf-8')

    def _load_sql(self, stack):
        """Loading the SQL is done by executing the the statements from the
        sql dump file.
        """
        if not stack.get('has_sql', True):
            return

        self._ensure_sql_database_is_empty()
        sql_file = stack['path'].joinpath('dump.sql')
        sql_statements = ['DROP TABLE IF EXISTS opengever_upgrade_version']
        sql_statements.extend(re.split(r';\n', sql_file.bytes().decode('utf-8')))
        session = create_session()
        map(session.execute, map(text, sql_statements))
        transaction.commit()

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
        data_file = stack['path'].joinpath('data.json')
        data_file.write_bytes(json_dumps(self.data).decode('utf-8'))

    def _load_data_from(self, stack):
        """Load any additional data from the stack.
        """
        data_file = stack['path'].joinpath('data.json')
        self.data = json_loads(data_file.bytes())

    def _dump_cachekey(self, stack):
        """Dump the cachekey for a stack.
        """
        cachekey_file = stack['path'].joinpath('cachekey.json')
        cachekey_file.write_bytes(json_dumps(stack['cachekey']).decode('utf-8'))

    def _load_cachekey(self, stack):
        """Load the cachekey for a stack.
        """
        cachekey_file = stack['path'].joinpath('cachekey.json')
        return json_loads(cachekey_file.bytes())


DB_CACHE_MANAGER = DBCacheManager()


class CachedStartup(Startup):

    def setUpDatabase(self):
        zodbDB = DB_CACHE_MANAGER.load_from_cache()
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


CACHED_STARTUP = CachedStartup()


class CachedPloneFixture(PloneFixture):
    defaultBases = (CACHED_STARTUP,)

    def setUp(self):
        super(CachedPloneFixture, self).setUp()
        DB_CACHE_MANAGER.dump_to_cache(self['zodbDB'], CACHE_PLONE_SETUP)

    def setUpDefaultContent(self, app):
        if not DB_CACHE_MANAGER.is_loaded_from_cache(CACHE_PLONE_SETUP):
            super(CachedPloneFixture, self).setUpDefaultContent(app)
        else:
            DB_CACHE_MANAGER.apply_cache_fixes(CACHE_PLONE_SETUP)

    def tearDownProducts(self, app):
        """Tear down products should not be necessary:
        we are trashing the database and isolating the z3 component registry.
        """


CACHED_PLONE_FIXTURE = CachedPloneFixture()
CACHED_COMPONENT_REGISTRY_ISOLATION = ComponentRegistryIsolationLayer(
    bases=(CACHED_PLONE_FIXTURE,),
    name='CACHED_COMPONENT_REGISTRY_ISOLATION')


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
