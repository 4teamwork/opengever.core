from ftw.dictstorage.sql import DictStorageModel
from opengever.base import model
from opengever.base.model import create_session
from opengever.ogds.base.setup import create_sql_tables
from plone.testing import Layer
from sqlalchemy.pool import StaticPool
from z3c.saconfig import EngineFactory
from z3c.saconfig import GloballyScopedSession
from z3c.saconfig.interfaces import IEngineFactory
from z3c.saconfig.interfaces import IScopedSession
from zope.component import provideUtility
from zope.sqlalchemy import datamanager
from zope.sqlalchemy import ZopeTransactionExtension
import transaction


class SQLiteMemoryFixture(Layer):
    """The sqlite memory fixture provides an in-memory sqlite database
    globally.
    Its designed to be used with the OpengeverFixture.
    The data is purged for each test since there is no isolation.
    All threads use the same connection and transaction.
    """

    def setUp(self):
        setup_memory_database()

    def testSetUp(self):
        create_tables()

    def testTearDown(self):
        # Tear down the sql session because we use the keep_session flag.
        model.Session.close_all()
        truncate_tables()


SQLITE_MEMORY_FIXTURE = SQLiteMemoryFixture()


class StandaloneMemoryDBLayer(Layer):
    """A Layer which only set up a test sqlite db in to the memory,
    but not a Plone.
    """

    def testSetUp(self):
        super(StandaloneMemoryDBLayer, self).testSetUp()
        create_tables()
        self.session = create_session()

    def testTearDown(self):
        model.Session.close_all()
        truncate_tables()
        transaction.abort()


def setup_memory_database():
    """Sets up a fresh in-memory database and activates it globally.
    """
    engine_factory = EngineFactory(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool)
    provideUtility(
        engine_factory, provides=IEngineFactory, name=u'opengever_db')

    # keep_session is necessary so that the builders can commit the
    # transaction multiple times and we can still use the sql objects
    # without fetching fresh copies.
    # The session should be closed on test tear down.
    scoped_session = GloballyScopedSession(
        engine=u'opengever_db',
        extension=ZopeTransactionExtension(keep_session=True))
    provideUtility(
        scoped_session, provides=IScopedSession, name=u'opengever')


def create_tables():
    """Creates the sql tables and makes sqlite specific configurations.
    """
    create_sql_tables()

    # Create opengever.globalindex SQL tables
    model.Base.metadata.create_all(create_session().bind)

    # Activate savepoint "support" for sqlite
    # We need savepoint support for version retrieval with CMFEditions.
    if 'sqlite' in datamanager.NO_SAVEPOINT_SUPPORT:
        datamanager.NO_SAVEPOINT_SUPPORT.remove('sqlite')


def truncate_tables():
    """Truncate existing tables in an sqlite way.
    """
    tables = (
        model.Base.metadata.tables.values()
        + DictStorageModel.metadata.tables.values()
    )

    session = create_session()
    for table in tables:
        session.execute(table.delete())
