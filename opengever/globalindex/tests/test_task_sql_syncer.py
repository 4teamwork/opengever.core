from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.globalindex import Session
from opengever.globalindex.model.task import Task
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import get_current_org_unit
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class TestTaskSQLSyncer(FunctionalTestCase):

    def setUp(self):
        super(TestTaskSQLSyncer, self).setUp()

        self.dossier = create(Builder('dossier')
                              .titled(u'dossier'))
        self.subdossier = create(Builder('dossier')
                                 .titled(u'subdossier')
                                 .within(self.dossier))
        self.task = create(
            Builder('task')
            .having(title=u'Mach mau!',
                    issuer=self.user.userid,
                    task_type='direct-execution',
                    responsible_client=get_current_org_unit().id(),
                    responsible=self.user.userid,
                    is_private=True,
                    deadline=date(2010, 1, 1),
                    text='Lorem ipsum dolor sit amet, consectetur')
            .within(self.subdossier)
        )

    def test_sql_task_is_created_on_plone_object_creation(self):
        self.assertEqual(1, Session.query(Task).count())
        task = Session.query(Task).one()
        self.assertEqual(get_current_org_unit().id(), task.assigned_org_unit)
        self.assertEqual(get_current_org_unit().id(), task.issuing_org_unit)
        self.assertEqual(get_current_admin_unit().id(), task.admin_unit_id)
        self.assertEqual(u'Mach mau!', task.title)
        self.assertEqual(self.user.userid, task.issuer)
        self.assertTrue(task.is_private)
        self.assertEqual(self.user.userid, task.responsible)
        self.assertEqual(u'dossier > subdossier > Mach mau!',
                         task.breadcrumb_title)
        self.assertEqual(u'task-state-open', task.review_state)
        self.assertEqual(u'dossier-1/dossier-2/task-1', task.physical_path)
        self.assertIsNotNone(task.icon)
        self.assertEqual(task.deadline, date(2010, 1, 1))
        self.assertIsNotNone(task.modified)
        self.assertEqual('direct-execution', task.task_type)
        self.assertFalse(task.is_subtask)
        self.assertEqual(1, task.sequence_number)
        self.assertEqual('Client1 / 1.1', task.reference_number)
        self.assertEqual('dossier', task.containing_dossier)
        self.assertEqual('subdossier', task.containing_subdossier)
        self.assertEqual(2, task.dossier_sequence_number)
        self.assertEqual('Lorem ipsum dolor sit amet, consectetur', task.text)
        self.assertSequenceEqual([TEST_USER_ID], task.principals)
        self.assertIsNone(task.predecessor)

    def test_sql_task_is_updated_on_plone_object_update(self):
        self.task.responsible_client = 'asd'
        self.task.title = u'Gopf, iz mach mau'
        notify(ObjectModifiedEvent(self.task))

        self.assertEqual(1, Session.query(Task).count())
        task = Session.query(Task).one()

        self.assertEqual('asd', task.assigned_org_unit)
        self.assertEqual(u'dossier > subdossier > Gopf, iz mach mau',
                         task.breadcrumb_title)
        self.assertEqual(u'Gopf, iz mach mau', task.title)

        self.assertEqual(get_current_org_unit().id(), task.issuing_org_unit)
        self.assertEqual(get_current_admin_unit().id(), task.admin_unit_id)
        self.assertEqual(self.user.userid, task.issuer)
        self.assertEqual(self.user.userid, task.responsible)
        self.assertEqual(u'task-state-open', task.review_state)
        self.assertEqual(u'dossier-1/dossier-2/task-1', task.physical_path)
        self.assertIsNotNone(task.icon)
        self.assertEqual(task.deadline, date(2010, 1, 1))
        self.assertIsNotNone(task.modified)
        self.assertEqual('direct-execution', task.task_type)
        self.assertFalse(task.is_subtask)
        self.assertEqual(1, task.sequence_number)
        self.assertEqual('Client1 / 1.1', task.reference_number)
        self.assertEqual('dossier', task.containing_dossier)
        self.assertEqual('subdossier', task.containing_subdossier)
        self.assertEqual(2, task.dossier_sequence_number)
        self.assertEqual('Lorem ipsum dolor sit amet, consectetur', task.text)
        self.assertSequenceEqual([TEST_USER_ID], task.principals)
        self.assertIsNone(task.predecessor)

    def test_sql_task_is_updated_when_task_is_moved(self):
        dossier2 = create(Builder('dossier')
                          .titled(u'Dossier 2'))
        subdossier2 = create(Builder('dossier')
                             .titled(u'Subdossier 2')
                             .within(dossier2))

        api.content.move(source=self.task, target=subdossier2)

        task = Session.query(Task).one()
        self.assertEqual('Subdossier 2', task.containing_subdossier)
        self.assertEqual(u'dossier-3/dossier-4/task-1', task.physical_path)
        self.assertEqual(4, task.dossier_sequence_number)
        self.assertEqual(u'Client1 / 2.1', task.reference_number)

    def test_sql_task_is_updated_when_container_is_moved(self):
        dossier2 = create(Builder('dossier')
                          .titled(u'Dossier 2'))

        api.content.move(source=self.subdossier, target=dossier2)

        task = Session.query(Task).one()
        self.assertEqual('subdossier', task.containing_subdossier)
        self.assertEqual(u'dossier-3/dossier-2/task-1', task.physical_path)
        self.assertEqual(2, task.dossier_sequence_number)
        self.assertEqual(u'Client1 / 2.1', task.reference_number)
