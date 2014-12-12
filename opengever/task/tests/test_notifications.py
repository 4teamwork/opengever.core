from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity.models.activity import Activity
from opengever.activity.utils import notification_center
from opengever.globalindex.oguid import Oguid
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
from zope.i18n import translate


class TestTaskNotifications(FunctionalTestCase):

    def setUp(self):
        super(TestTaskNotifications, self).setUp()

        self.hugo = create(Builder('ogds_user')
                           .id('hugo.boss')
                           .assign_to_org_units([self.org_unit])
                           .having(firstname=u'Hugo', lastname=u'Boss'))

        self.peter = create(Builder('ogds_user')
                            .id('peter.mueller')
                            .assign_to_org_units([self.org_unit])
                            .having(firstname=u'Peter', lastname=u'Mueller'))

        self.dossier = create(Builder('dossier').titled(u'Dossier'))

    @browsing
    def test_ervery_task_transtition_add_an_activityn(self, browser):
        task = create(Builder('task').titled(u'Test t\xe4sk'))

        browser.login().open(task)
        browser.css('#workflow-transition-task-transition-open-in-progress').first.click()
        browser.fill({'Response':'Ok I will do that for you!'})
        browser.css('#form-buttons-save').first.click()

        activity = Activity.query.all()[0]

        self.assertEquals(u'task-transition-open-in-progress', activity.kind)
        self.assertEquals(TEST_USER_ID, activity.actor_id)
        self.assertEquals(u'Test t\xe4sk', activity.title)
        self.assertEquals(u'transition_label_accept', activity.summary)
        self.assertEquals('Ok I will do that for you!', activity.description)
        self.assertEquals(Oguid.for_object(task), activity.resource.oguid)

    @browsing
    def test_adding_a_task_adds_issuer_and_responsible_to_watcher(self, browser):
        browser.login().open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title':'Test task',
                      'Task Type':u'comment',
                      'Responsible':u'hugo.boss',
                      'Issuer': u'peter.mueller'})

        browser.css('#form-buttons-save').first.click()

        task = self.dossier.listFolderContents()[0]

        self.assertEquals(
            ['hugo.boss', 'peter.mueller'],
            [watcher.user_id for watcher in notification_center().get_watchers(task)])

    @browsing
    def test_adding_a_task_adds_activity(self, browser):
        browser.login().open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title':'Test task',
                      'Task Type':u'comment',
                      'Responsible':u'hugo.boss',
                      'Issuer': u'peter.mueller'})

        browser.css('#form-buttons-save').first.click()

        task = self.dossier.listFolderContents()[0]

        activity = Activity.query.all()[0]
        self.assertEquals(u'task-added', activity.kind)
        self.assertEquals(TEST_USER_ID, activity.actor_id)
        self.assertEquals(u'Test task', activity.title)
        self.assertEquals(u'transition_label_created', activity.summary)
        self.assertEquals(Oguid.for_object(task), activity.resource.oguid)
