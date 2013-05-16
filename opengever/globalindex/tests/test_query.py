from opengever.globalindex.interfaces import ITaskQuery
from opengever.globalindex.model import Base
from opengever.globalindex.model.task import Task
from opengever.globalindex.query import TaskQuery
from opengever.testing import FunctionalTestCase
from z3c.saconfig import EngineFactory
from z3c.saconfig import GloballyScopedSession
from z3c.saconfig import named_scoped_session
from z3c.saconfig.interfaces import IEngineFactory
from z3c.saconfig.interfaces import IScopedSession
from zope.component import getUtility
from zope.component import provideUtility


class TestTaskQuery(FunctionalTestCase):

    def test_query(self):
        # Register a named scoped session utility.
        engine_factory = EngineFactory('sqlite:///:memory:')
        provideUtility(engine_factory, provides=IEngineFactory, name=u'opengever_db')
        scoped_session = GloballyScopedSession(engine=u'opengever_db')
        provideUtility(scoped_session, provides=IScopedSession, name=u'opengever')

        # Register the TaskQuery utility.
        provideUtility(TaskQuery())
        query = getUtility(ITaskQuery)

        # Get db session and create tables.
        Session = named_scoped_session("opengever")
        session = Session()
        Base.metadata.create_all(session.bind)

        # Add some tasks.
        t1 = Task(1, 'm1')
        t1.responsible = 'Responsible 1'
        t1.issuer = 'Issuer 1'
        t1.physical_path = 'ordnungssystem/kernbereich-3/dossier-4/task-1/'
        session.add(t1)
        t2 = Task(2, 'm1')
        t2.responsible = 'Responsible 2'
        t2.issuer = 'Issuer 1'
        t2.physical_path = 'ordnungssystem/allgemein/dossier-2/task-2/'
        session.add(t2)
        t3 = Task(3, 'm2')
        t3.responsible = 'Responsible 1'
        t3.issuer = 'Issuer 2'
        t3.physical_path = 'ordnungssystem/allgemein/dossier-16/task-3/'
        session.add(t3)

        # Query for task by int_id and client_id.
        self.assertEquals(t3, query.get_task(3, 'm2'))
        self.assertEquals(None, query.get_task(1, 'm2'))

        # Query for tasks by responsible.
        self.assertEquals([t1, t3],
            query.get_tasks_for_responsible('Responsible 1'))
        self.assertEquals([],
            query.get_tasks_for_responsible('Responsible 3'))

        # Query for tasks by issuer.
        self.assertEquals([t1, t2], query.get_tasks_for_issuer('Issuer 1'))
        self.assertEquals([], query.get_tasks_for_issuer('Issuer 3'))

        # Query for task by path
        self.assertEquals(t1, query.get_task_by_path(
            'ordnungssystem/kernbereich-3/dossier-4/task-1/', 'm1'))
        self.assertEquals(None, query.get_task_by_path(
            'ordnungssystem/allgemein/dossier-16/task-3/', 'm1'))
        self.assertEquals(None, query.get_task_by_path(
            'ordnungssystem/not-existing/task-3/', 'm1'))

        # Query for tasks by paths
        self.assertEquals(
            [t1, t2, t3],
            query.get_tasks_by_paths(
                ['ordnungssystem/kernbereich-3/dossier-4/task-1/',
                 'ordnungssystem/allgemein/dossier-2/task-2/',
                 'ordnungssystem/allgemein/dossier-16/task-3/'])
        )
        self.assertEquals(
            [t1, t3],
            query.get_tasks_by_paths(
                ['ordnungssystem/kernbereich-3/dossier-4/task-1/',
                 'ordnungssystem/not-existing/task-1/',
                 'ordnungssystem/allgemein/dossier-16/task-3/'])
        )
