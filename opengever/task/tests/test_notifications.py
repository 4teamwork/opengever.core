from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity.models.activity import Activity
from opengever.activity.utils import notification_center
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
from opengever.globalindex.oguid import Oguid


class TestTaskNotifications(FunctionalTestCase):

    @browsing
    def test_ervery_task_transtition_add_an_activity(self, browser):
        task = create(Builder('task').titled(u'Test t\xe4sk'))
        browser.login().open(task)
        browser.css('#workflow-transition-task-transition-open-in-progress').first.click()
        browser.fill({'Response':'Ok I will do that for you!'})
        browser.css('#form-buttons-save').first.click()

        activity = Activity.query.all()[0]

        self.assertEquals(u'task-transition-open-in-progress', activity.kind)
        self.assertEquals(TEST_USER_ID, activity.actor_id)
        self.assertEquals(u'transition_label_accept', activity.title)
        self.assertEquals('Ok I will do that for you!', activity.description)
        self.assertEquals(Oguid.for_object(task), activity.resource.oguid)
