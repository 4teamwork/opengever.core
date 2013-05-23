from opengever.core.testing import setup_sql_tables
from opengever.core.testing import truncate_sql_tables
from opengever.ogds.base.utils import create_session
from plone.testing import Layer
from z3c.saconfig import EngineFactory
from z3c.saconfig import GloballyScopedSession
from z3c.saconfig.interfaces import IEngineFactory
from z3c.saconfig.interfaces import IScopedSession
from zope.component import provideUtility


class MemoryDBLayer(Layer):
    """A Layer which only set up a test sqlite db in to the memory
    """

    def testSetUp(self):
        super(MemoryDBLayer, self).testSetUp()

        engine_factory = EngineFactory('sqlite:///:memory:')
        provideUtility(
            engine_factory, provides=IEngineFactory, name=u'opengever_db')

        scoped_session = GloballyScopedSession(engine=u'opengever_db')
        provideUtility(
            scoped_session, provides=IScopedSession, name=u'opengever')

        setup_sql_tables()
        self.session = create_session()

    def testTearDown(test):
        truncate_sql_tables()

MEMORY_DB_LAYER = MemoryDBLayer()
