from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.utils import get_header
from ftw.testbrowser import browsing
from ftw.testing.mailing import Mailing
from opengever.activity.hooks import insert_notification_defaults
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER
from opengever.testing import FunctionalTestCase
import email


class TestEmailNotification(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER

    def setUp(self):
        super(TestEmailNotification, self).setUp()
        # setup mail
        Mailing(self.portal).set_up()

        self.hugo = create(Builder('ogds_user')
                           .assign_to_org_units([self.org_unit])
                           .having(userid='hugo.boss',
                                   firstname='Hugo',
                                   lastname='Boss',
                                   email='hugo.boss@example.org'))

        self.franz = create(Builder('ogds_user')
               .assign_to_org_units([self.org_unit])
               .having(userid='franz.michel',
                       firstname='Franz',
                       lastname='Michel',
                       email='franz.michel@example.org'))

        create(Builder('watcher').having(actorid='hugo.boss'))

        self.dossier = create(Builder('dossier').titled(u'Dossier A'))

        insert_notification_defaults(self.portal)

    def tearDown(self):
        super(TestEmailNotification, self).tearDown()
        Mailing(self.layer['portal']).tear_down()

    @browsing
    def test_subject_is_title(self, browser):
        browser.login().open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title': 'Test Task',
                      'Task Type': 'comment'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.org_unit.id() + ':hugo.boss')

        browser.css('#form-buttons-save').first.click()

        mail = email.message_from_string(Mailing(self.portal).pop())

        self.assertEquals('GEVER Task: Test Task', mail.get('Subject'))

    @browsing
    def test_from_and_to_addresses(self, browser):
        browser.login().open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title': 'Test Task',
                      'Task Type': 'comment'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.org_unit.id() + ':hugo.boss')
        browser.css('#form-buttons-save').first.click()

        mail = email.message_from_string(Mailing(self.portal).pop())
        self.assertEquals('hugo.boss@example.org', mail.get('To'))
        self.assertEquals(
            'Test User <test@example.org>', get_header(mail, 'From'))

    @browsing
    def test_task_title_is_linked_to_resolve_notification_view(self, browser):
        browser.login().open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title': 'Test Task',
                      'Task Type': 'comment'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.org_unit.id() + ':hugo.boss')
        browser.css('#form-buttons-save').first.click()

        mail = email.message_from_string(Mailing(self.portal).pop())
        html_part = mail.get_payload()[0].as_string()

        link = '<p><a href=3D"http://example.com/@@resolve_notification' \
               '?notification_id=\n=3D1">Test Task</a></p>'

        self.assertIn(link, html_part)

    @browsing
    def test_mail_dispatcher_respects_dispatcher_roles(self, browser):
        """By default only the responsible should be notified by mail, when
        a task gets added.
        """
        browser.login().open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title': 'Test Task',
                      'Task Type': 'comment'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.org_unit.id() + ':hugo.boss')
        browser.css('#form-buttons-save').first.click()

        self.assertEquals(1, len(Mailing(self.portal).get_messages()))
        mail = email.message_from_string(Mailing(self.portal).pop())
        self.assertEquals(
            'hugo.boss@example.org', get_header(mail, 'To'))

    @browsing
    def test_mail_dispatcher_respects_dispatcher_roles_even_if_its_a_group(self, browser):
        """By default only the responsible should be notified by mail, when
        a task gets added.
        """

        inbox_group = self.org_unit.inbox_group
        inbox_group.users.append(self.hugo)
        inbox_group.users.append(self.franz)

        browser.login().open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title': 'Test Task',
                      'Issuer': 'inbox:client1',
                      'Task Type': 'comment'})
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(
            self.org_unit.id() + ':franz.michel')

        browser.css('#form-buttons-save').first.click()

        self.assertEquals(1, len(Mailing(self.portal).get_messages()))
        mail = email.message_from_string(Mailing(self.portal).pop())
        self.assertEquals(
            'franz.michel@example.org', get_header(mail, 'To'))
