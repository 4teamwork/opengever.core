from datetime import date
from opengever.base.model import Session
from opengever.globalindex.model.task import Task
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import get_current_org_unit
from opengever.testing import IntegrationTestCase
from plone import api
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class TestTaskSQLSyncer(IntegrationTestCase):

    def test_sql_task_is_created_on_plone_object_creation(self):
        self.login(self.regular_user)
        self.assertEqual(14, Session.query(Task).count())
        # self.private_task
        task = Session.query(Task).filter(
            Task.title == u'Diskr\xe4te Dinge').one()
        self.assertEqual(get_current_org_unit().id(), task.assigned_org_unit)
        self.assertEqual(get_current_org_unit().id(), task.issuing_org_unit)
        self.assertEqual(get_current_admin_unit().id(), task.admin_unit_id)
        self.assertEqual(u'Diskr\xe4te Dinge', task.title)
        self.assertEqual(self.dossier_responsible.getId(), task.issuer)
        self.assertTrue(task.is_private)
        self.assertEqual(self.regular_user.getId(), task.responsible)
        expected_breadcrumbs = (
            u'Ordnungssystem'
            u' > 1. F\xfchrung'
            u' > 1.1. Vertr\xe4ge und Vereinbarungen'
            u' > Vertr\xe4ge mit der kantonalen Finanzverwaltung'
            u' > Diskr\xe4te Dinge'
        )  # Do not add commas here - this is a string!
        self.assertEqual(expected_breadcrumbs, task.breadcrumb_title)
        self.assertEqual('task-state-in-progress', task.review_state)
        expected_path = (
            'ordnungssystem'
            '/fuhrung'
            '/vertrage-und-vereinbarungen'
            '/dossier-1'
            '/task-12'
        )  # Do not add commas here - this is a string!
        self.assertEqual(expected_path, task.physical_path)
        self.assertIsNotNone(task.icon)
        self.assertEqual(task.deadline, date(2020, 1, 1))
        self.assertIsNotNone(task.modified)
        self.assertEqual('direct-execution', task.task_type)
        self.assertFalse(task.is_subtask)
        self.assertEqual(12, task.sequence_number)
        self.assertEqual('Client1 1.1 / 1', task.reference_number)
        self.assertEqual(
            u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            task.containing_dossier,
        )
        self.assertEqual('', task.containing_subdossier)
        self.assertEqual(1, task.dossier_sequence_number)
        self.assertEqual(
            u'L\xf6rem ipsum dolor sit amet, consectetur', task.text)
        expected_principals = [
            get_current_org_unit().users_group.id(), self.regular_user.getId()]
        self.assertItemsEqual(expected_principals, task.principals)
        self.assertIsNone(task.predecessor)

    def test_sql_task_is_updated_on_plone_object_update(self):
        self.login(self.regular_user)
        self.task.responsible_client = 'asd'
        self.task.title = u'G\xf6pf, iz mach mau'
        notify(ObjectModifiedEvent(self.task))

        self.assertEqual(14, Session.query(Task).count())
        task = Session.query(Task).filter(
            Task.title == u'G\xf6pf, iz mach mau').one()

        self.assertEqual('asd', task.assigned_org_unit)
        expected_breadcrumbs = (
            u'Ordnungssystem'
            u' > 1. F\xfchrung'
            u' > 1.1. Vertr\xe4ge und Vereinbarungen'
            u' > Vertr\xe4ge mit der kantonalen Finanzverwaltung'
            u' > G\xf6pf, iz mach mau'
        )  # Do not add commas here - this is a string!
        self.assertEqual(expected_breadcrumbs, task.breadcrumb_title)
        self.assertEqual(u'G\xf6pf, iz mach mau', task.title)

        self.assertEqual(get_current_org_unit().id(), task.issuing_org_unit)
        self.assertEqual(get_current_admin_unit().id(), task.admin_unit_id)
        self.assertEqual(self.dossier_responsible.getId(), task.issuer)
        self.assertEqual(self.regular_user.getId(), task.responsible)
        self.assertEqual('task-state-in-progress', task.review_state)
        expected_path = (
            'ordnungssystem'
            '/fuhrung'
            '/vertrage-und-vereinbarungen'
            '/dossier-1'
            '/task-1'
        )  # Do not add commas here - this is a string!
        self.assertEqual(expected_path, task.physical_path)
        self.assertIsNotNone(task.icon)
        self.assertEqual(task.deadline, date(2016, 11, 1))
        self.assertIsNotNone(task.modified)
        self.assertEqual('correction', task.task_type)
        self.assertFalse(task.is_subtask)
        self.assertEqual(1, task.sequence_number)
        self.assertEqual('Client1 1.1 / 1', task.reference_number)
        self.assertEqual(
            u'Vertr\xe4ge mit der kantonalen Finanzverwaltung', task.containing_dossier)
        self.assertEqual('', task.containing_subdossier)
        self.assertEqual(1, task.dossier_sequence_number)
        self.assertIsNone(task.text)
        expected_principals = [
            get_current_org_unit().users_group.id(), self.regular_user.getId()]
        self.assertItemsEqual(expected_principals, task.principals)
        self.assertIsNone(task.predecessor)

    def test_sql_task_is_updated_when_task_is_moved(self):
        self.login(self.regular_user)
        api.content.move(source=self.task, target=self.subdossier)

        # self.task
        task = Session.query(Task).filter(
            Task.title == u'Vertragsentwurf \xdcberpr\xfcfen').one()
        self.assertEqual(
            u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            task.containing_dossier,
        )
        self.assertEqual('2016', task.containing_subdossier)
        expected_path = (
            'ordnungssystem'
            '/fuhrung'
            '/vertrage-und-vereinbarungen'
            '/dossier-1'
            '/dossier-2'
            '/task-1'
        )  # Do not add commas here - this is a string!
        self.assertEqual(expected_path, task.physical_path)
        self.assertEqual(2, task.dossier_sequence_number)
        self.assertEqual('Client1 1.1 / 1.1', task.reference_number)

    def test_sql_task_is_updated_when_container_is_moved(self):
        self.login(self.regular_user)
        api.content.move(source=self.dossier, target=self.empty_dossier)

        # self.task
        task = Session.query(Task).filter(
            Task.title == u'Vertragsentwurf \xdcberpr\xfcfen').one()
        self.assertEqual(u'An empty dossier', task.containing_dossier)
        self.assertEqual(
            u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
            task.containing_subdossier,
        )
        expected_path = (
            'ordnungssystem'
            '/fuhrung'
            '/vertrage-und-vereinbarungen'
            '/dossier-7'
            '/dossier-1'
            '/task-1'
        )  # Do not add commas here - this is a string!
        self.assertEqual(expected_path, task.physical_path)
        self.assertEqual(1, task.dossier_sequence_number)
        self.assertEqual('Client1 1.1 / 4.1', task.reference_number)
