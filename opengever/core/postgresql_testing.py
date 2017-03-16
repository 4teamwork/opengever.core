from ftw.dictstorage.sql import DictStorageModel
from opengever.base import model
from opengever.ogds.models import BASE
from plone.testing import Layer
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.orm import create_session
from sqlalchemy_utils import create_database
from sqlalchemy_utils import database_exists
from sqlalchemy_utils import drop_database
from z3c.saconfig.interfaces import IScopedSession
from z3c.saconfig.utility import GloballyScopedSession
from zope.component import provideUtility
import os


class PostgreSQLFixture(Layer):
    """Fixture for running Plone tests against a PostgreSQL database.
    It designed to be used with the OpengeverFixture.
    """

    def setUp(self):
        self.matroska = Matroska()

    def testSetUp(self):
        self.matroska.push()

    def testTearDown(self):
        self.matroska.pop()

    def tearDown(self):
        model.Session.close_all()
        model.Session.registry.clear()



POSTGRES_FIXTURE = PostgreSQLFixture()


class Matroska(object):
    """The matroska lets us implement an sql isolation by copying the
    database into new generations and switch back to the original.
    """

    def __init__(self):
        engine = create_engine(new_engine_url())
        create_database(engine.url)
        create_tables(engine)
        self.generation = MatroskaGeneration(None, engine).activate()

    def push(self):
        self.generation = self.generation.fork()

    def pop(self):
        self.generation = self.generation.uninstall()


class MatroskaGeneration(object):
    """A matroska generation represents exactly one database / engine.
    It can be forked, which makes a copy of data and sequences into a
    new database.
    """

    def __init__(self, parent, engine):
        self.parent = parent
        self.engine = engine
        self._disposed_engine = None

    def fork(self):
        """Fork this generation with all its data into a new database.
        """
        if self._disposed_engine is not None:
            # We have a disposed engine with the same data as this
            # generation, so lets reuse it.
            engine = self._disposed_engine
            self._disposed_engine = None

        else:
            engine = create_engine(new_engine_url())
            create_database(engine.url)
            create_tables(engine)
            copy_data(self.engine, engine)
            copy_sequences(self.engine, engine)

        return MatroskaGeneration(self, engine).activate()

    def activate(self):
        TestingScopedSession.install(self.engine)
        return self

    def uninstall(self):
        if self._disposed_engine:
            drop_database(self._disposed_engine)
            self._disposed_engine = None

        if self.parent is None:
            # root generation
            drop_database(self.engine.url)
            return

        if False:
            # transaction rollback / abort
            self.parent.dispose(self)
        else:
            drop_database(self.engine.url)

        return self.parent.activate()

    def dispose(self, fork):
        """
        A fork of our generation is disposed because nothing was changed.
        Keep it for reuse later.
        """
        assert fork.parent == self, 'MatroskaGeneration mess: not my fork.'
        self._disposed_engine = fork.engine


class TestingScopedSession(GloballyScopedSession):

    def __init__(self, engine):
        self.engine = engine
        super(TestingScopedSession, self).__init__()

    def sessionFactory(self):
        kw = self.kw.copy()
        kw['bind'] = self.engine
        return create_session(**kw)

    @classmethod
    def install(klass, engine):
        provideUtility(klass(engine), provides=IScopedSession, name=u'opengever')
        model.Session.bind = engine


def new_engine_url():
    """Create a postgresql engine URL with a new database name.
    Makes sure that the database name is unique over the lieftime
    of the process.
    """
    counter = globals()['_db_counter'] = globals().get('_db_counter', 0) + 1
    database_name = 'opengever_test_{}_{}'.format(os.getpid(), counter)
    url = 'postgresql+psycopg2:///{}'.format(database_name)
    if database_exists(url):
        drop_database(url)
    return url


def get_tables_of_engine(engine):
    """Return the tables for an engine.
    """
    metadata = MetaData(engine)
    metadata.reflect()
    return metadata.sorted_tables


def create_tables(engine):
    """Create SQL tables in an engine.
    """
    model.Base.metadata.create_all(engine)
    BASE.metadata.create_all(engine)
    DictStorageModel.metadata.create_all(engine)


def copy_data(source_engine, target_engine):
    """Copy all data from one engine to antother.
    The tables must be set up on the target.
    """

    for table in get_tables_of_engine(source_engine):
        data = [{column.key: row[column.name] for column in table.c}
                for row
                in source_engine.execute(table.select())]

        if data:
            target_engine.execute(table.insert(), data)

def copy_sequences(source_engine, target_engine):
    """Copy sequences from one engine to antother.
    """
    if not source_engine.dialect.supports_sequences:
        return

    parent_sequence_names = source_engine.execute(
        "SELECT c.relname "
        "FROM pg_class c "
        "WHERE c.relkind = 'S'").fetchall()

    for sequence_name in parent_sequence_names:
        # Get the last_value from a parent matroska sequence
        parent_last_value = source_engine.execute(
            "SELECT last_value FROM {0}"
            .format(sequence_name[0])).fetchall()

        # Reset the new matroska sequence to + 1
        # https://www.postgresql.org/docs/current/static/sql-altersequence.html
        target_engine.execute(
            "ALTER SEQUENCE {0} RESTART WITH {1};"
            .format(sequence_name[0],
                    parent_last_value[0][0] + 1))
