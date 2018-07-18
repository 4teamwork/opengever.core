from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.globalindex.model.reminder_settings import ReminderSetting
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
