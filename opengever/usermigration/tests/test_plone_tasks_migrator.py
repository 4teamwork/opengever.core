from ftw.builder import Builder
from ftw.builder import create
from opengever.base.response import IResponseContainer
from opengever.task.reminder import Reminder
from opengever.task.reminder.interfaces import IReminderStorage
from opengever.task.reminder.storage import REMINDER_ANNOTATIONS_KEY
from opengever.task.task_response import TaskResponse
from opengever.testing import FunctionalTestCase
from opengever.usermigration.plone_tasks import PloneTasksMigrator
from zope.annotation import IAnnotations


class TestPloneTasksMigrator(FunctionalTestCase):

    def setUp(self):
        super(TestPloneTasksMigrator, self).setUp()
        self.portal = self.layer['portal']

        self.old_ogds_user = create(Builder('ogds_user')
                                    .id('HANS.MUSTER')
                                    .having(active=False))
        self.new_ogds_user = create(Builder('ogds_user')
                                    .id('hans.muster')
                                    .having(active=True))

    def test_migrates_plone_task_responsibles(self):
        task = create(Builder('task')
                      .having(responsible='HANS.MUSTER'))

        PloneTasksMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        self.assertEquals('hans.muster', task.responsible)

    def test_migrates_plone_task_issuers(self):
        task = create(Builder('task')
                      .having(issuer='HANS.MUSTER'))

        PloneTasksMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        self.assertEquals('hans.muster', task.issuer)

    def test_migrates_plone_task_response_creator(self):
        task = create(Builder('task'))

        response = TaskResponse()
        response.creator = 'HANS.MUSTER'
        IResponseContainer(task).add(response)

        PloneTasksMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        self.assertEquals('hans.muster', response.creator)

    def test_migrates_plone_task_responsible_before(self):
        task = create(Builder('task'))

        response = TaskResponse()
        response.add_change('responsible', 'HANS.MUSTER', 'peter')
        IResponseContainer(task).add(response)

        PloneTasksMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        self.assertEquals('hans.muster', response.changes[-1]['before'])

    def test_migrates_plone_task_responsible_after(self):
        task = create(Builder('task'))

        response = TaskResponse()
        response.add_change('responsible', 'peter', 'HANS.MUSTER')
        IResponseContainer(task).add(response)

        PloneTasksMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        self.assertEquals('hans.muster', response.changes[-1]['after'])

    def test_migrates_plone_task_reminders(self):
        task = create(Builder('task'))
        reminders = IReminderStorage(task)
        reminders.set(Reminder.create('same_day'), user_id='HANS.MUSTER')

        PloneTasksMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        annotations = IAnnotations(task)
        reminders = annotations.get(REMINDER_ANNOTATIONS_KEY)

        self.assertIn('hans.muster', reminders)
        self.assertNotIn('HANS.MUSTER', reminders)
