from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browser
from ftw.testbrowser import browsing
from opengever.activity import notification_center
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER
from opengever.ogds.base.utils import ogds_service
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestPloneNotificationCenter(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER

    def setUp(self):
        super(TestPloneNotificationCenter, self).setUp()

        inbox_group = ogds_service().fetch_group(self.org_unit.inbox_group_id)

        create(Builder('ogds_user')
               .assign_to_org_units([self.org_unit])
               .in_group(inbox_group)
               .having(userid='hugo.boss',
                       firstname='Hugo',
                       lastname='Boss',
                       email='hugo.boss@example.org'))

        create(Builder('ogds_user')
               .assign_to_org_units([self.org_unit])
               .in_group(inbox_group)
               .having(userid='franz.michel',
                       firstname='Franz',
                       lastname='Michel',
                       email='hugo.boss@example.org'))

        self.dossier = create(Builder('dossier').titled(u'Dossier A'))

    @browsing
    def test_add_watcher_adds_every_actor_representatives(self, member):
        browser.login().open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title': 'Test Task',
                      'Responsible': 'inbox:client1',
                      'Task Type': 'comment'})
        browser.css('#form-buttons-save').first.click()

        task = self.dossier.get('task-1')
        watchers = notification_center().get_watchers(task)

        self.assertItemsEqual(
            [TEST_USER_ID, 'hugo.boss', 'franz.michel'],
            [watcher.user_id for watcher in watchers])
