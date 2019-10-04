from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.globalindex.model.reminder_settings import ReminderSetting
from opengever.task.reminder import ReminderOneWeekBefore
from opengever.testing import IntegrationTestCase


class TestReminderSettings(IntegrationTestCase):

    def test_model_representation(self):
        today = date.today()
        self.login(self.dossier_responsible)
        create(Builder('reminder_setting_model')
               .for_object(self.task)
               .for_actor(self.regular_user)
               .remind_on(today))

        self.assertEquals(
            '<ReminderSetting 1 for kathi.barfuss for {} on {} >'.format(
                self.task.get_sql_object(), today),
            repr(ReminderSetting.query.first()))

    def test_gets_added_when_syncing_a_task(self):
        self.login(self.dossier_responsible)
        self.task.set_reminder(ReminderOneWeekBefore.option_type)
        self.task.sync()

        self.assertEquals(1, ReminderSetting.query.count())
        setting = ReminderSetting.query.first()
        self.assertEquals(self.dossier_responsible.id, setting.actor_id)
        self.assertEquals(
            ReminderOneWeekBefore.option_type, setting.option_type)
        self.assertEquals(date(2016, 10, 25), setting.remind_day)

    def test_gets_updated_when_syncing_a_task(self):
        self.login(self.dossier_responsible)

        self.task.set_reminder(ReminderOneWeekBefore.option_type)
        self.task.sync()

        ReminderSetting.query.all()

        self.task.deadline = date(2018, 9, 28)
        self.task.sync()

        self.assertEquals(1, ReminderSetting.query.count())
        setting = ReminderSetting.query.first()
        self.assertEquals(date(2018, 9, 21), setting.remind_day)

    def test_gets_removed_when_syncing_a_task(self):
        self.login(self.dossier_responsible)
        self.task.set_reminder(ReminderOneWeekBefore.option_type)
        self.task.sync()

        self.assertEquals(1, ReminderSetting.query.count())

        self.task.clear_reminder(user_id=self.dossier_responsible.id)
        self.task.sync()

        self.assertEquals(0, ReminderSetting.query.count())
