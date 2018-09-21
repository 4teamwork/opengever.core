from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browser
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from ftw.testbrowser.pages.statusmessages import warning_messages
from opengever.activity import notification_center
from opengever.activity.hooks import insert_notification_defaults
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER
from opengever.ogds.base.utils import ogds_service
from opengever.testing import FunctionalTestCase
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
import transaction


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
    def test_add_watcher_adds_subscription_for_each_actor(self, member):
        browser.login().open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title': 'Test Task',
                      'Task Type': 'comment'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('inbox:org-unit-1')

        browser.css('#form-buttons-save').first.click()

        task = self.dossier.get('task-1')
        resource = notification_center().fetch_resource(task)

        subscriptions = resource.subscriptions

        self.assertItemsEqual(
            [(u'inbox:org-unit-1', u'task_responsible'),
             (u'test_user_1_', u'task_issuer')],
            [(sub.watcher.actorid, sub.role) for sub in subscriptions])


class TestNotifactionCenterErrorHandling(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER

    def setUp(self):
        super(TestNotifactionCenterErrorHandling, self).setUp()
        insert_notification_defaults(self.portal)
        create(Builder('user')
               .having(firstname='Hugo', lastname='Boss')
               .with_userid('hugo.boss'))

        setRoles(self.portal, 'hugo.boss',
                 ['Contributor', 'Editor', 'Reader'])
        transaction.commit()

        self.dossier = create(Builder('dossier').titled(u'Dossier A'))

    @browsing
    def test_successfully_add_activity(self, member):
        create(Builder('ogds_user')
               .having(userid='hugo.boss'))

        browser.login('hugo.boss').open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title': 'Test Task',
                      'Task Type': 'comment'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('inbox:org-unit-1')
        form.find_widget('Issuer').fill(TEST_USER_ID)

        browser.css('#form-buttons-save').first.click()

        self.assertEquals([], warning_messages())
        self.assertEquals(['Item created'], info_messages())

    @browsing
    def test_shows_message_if_dispatchers_raise_an_exception(self, member):
        create(Builder('ogds_user')
               .having(userid='hugo.boss', email=None)
               .in_group(self.org_unit.users_group))

        browser.login().open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title': 'Test Task',
                      'Task Type': 'comment'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('org-unit-1:hugo.boss')
        form.find_widget('Issuer').fill(TEST_USER_ID)

        browser.css('#form-buttons-save').first.click()

        self.assertEquals(
            ['A problem has occurred during the notification creation. '
             'Notification could not or only partially produced.'],
            warning_messages())
        self.assertEquals(['Item created'], info_messages())
