from ftw.builder import session
from ftw.builder.testing import BUILDER_LAYER
from opengever.ogds.models import BASE
from opengever.ogds.models.tests import builders  # keep!
from plone.testing import Layer
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker


class DatabaseLayer(Layer):

    defaultBases = (BUILDER_LAYER,)

    def __init__(self, *args, **kwargs):
        Layer.__init__(self, *args, **kwargs)
        self._engine = None
        self._session = None
        self.auto_commit = False

    def __call__(self):
        return self

    def setUp(self):
        self.old_factory = session.factory
        session.factory = self

    def tearDown(self):
        session.factory = self.old_factory

    def testSetUp(self):
        self.disconnect()
        self.get_connection()

    def testTearDown(self):
        self.disconnect()

    def get_connection(self):
        if not self._engine:
            self._engine = create_engine('sqlite://')

            # make like case sensitive, to have the same conditions as we have
            # with PostgreSQL in production
            self._engine.execute('PRAGMA case_sensitive_like = ON')

            BASE.metadata.bind = self._engine
            BASE.metadata.create_all()

        return self._engine

    def disconnect(self):
        self.close_session()
        self._engine = None

    @property
    def session(self):
        if not self._session:
            self._session = scoped_session(sessionmaker(
                    bind=self.get_connection()))
            BASE.session = self._session
        return self._session

    def close_session(self):
        if not self._session:
            return False

        else:
            self.session.close()
            self._session = None
            return True

    def commit(self):
        self.session.commit()


DATABASE_LAYER = DatabaseLayer()
