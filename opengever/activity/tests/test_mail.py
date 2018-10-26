from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.utils import get_header
from ftw.testbrowser import browsing
from ftw.testing.mailing import Mailing
from opengever.activity.roles import TASK_RESPONSIBLE_ROLE
from opengever.globalindex.model.task import Task
from opengever.testing import IntegrationTestCase
import email


class TestEmailNotification(IntegrationTestCase):

    features = (
        'activity',
        )

    def setUp(self):
        super(TestEmailNotification, self).setUp()
        # XXX - we cannot yet fixturize SQL objects
        create(Builder('watcher').having(actorid=self.regular_user.id))
        # XXX - we cannot yet fixturize SQL objects
        create(
            Builder('notification_setting')
            .having(
                kind='task-commented',
                userid=self.regular_user.getId(),
                mail_notification_roles=[TASK_RESPONSIBLE_ROLE],
                badge_notification_roles=[],
                digest_notification_roles=[],
                ),
            )
        # XXX - we cannot yet fixturize SQL objects
        # The secretariat user is a part of the inbox group
        create(Builder('watcher').having(actorid=self.secretariat_user.id))

    def create_task_via_browser(self, browser, inbox=False):
        browser.open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title': 'Test Task', 'Task Type': 'comment'})
        # XXX - we cannot yet fixturize SQL objects so we have to hardcode here
        org_unit_id = u'fa'
        form = browser.find_form_by_field('Responsible')
        responsible_id = u':'.join((org_unit_id, self.regular_user.id, ))
        form.find_widget('Responsible').fill(responsible_id)
        if inbox:
            # XXX - How to get the correct id from the fixtured objects?
            inbox_id = u':'.join(('inbox', org_unit_id, ))
            form.find_widget('Issuer').fill(inbox_id)
        browser.css('#form-buttons-save').first.click()

    @browsing
    def test_subject_is_title(self, browser):
        self.login(self.dossier_responsible, browser)
        self.create_task_via_browser(browser)
        mail = email.message_from_string(Mailing(self.portal).pop())
        self.assertEquals('GEVER Activity: Test Task', mail.get('Subject'))

    @browsing
    def test_notification_summary_is_split_into_paragraphs(self, browser):
        self.login(self.dossier_responsible, browser)
        self.create_task_via_browser(browser)
        # XXX - did not find a neater way to get the task quickly
        browser.open(Task.query.all()[-1], view='addcommentresponse')
        browser.fill({'Response': 'Multi\n\nline\ncomment'})
        browser.css('#form-buttons-save').first.click()
        mails = Mailing(self.portal).get_messages()
        self.assertEqual(len(mails), 2)
        raw_mail = mails[-1]
        self.assertIn('<p>Multi</p>', raw_mail)
        self.assertIn('<p></p>', raw_mail)
        self.assertIn('<p>line</p>', raw_mail)
        self.assertIn('<p>comment</p>', raw_mail)

    @browsing
    def test_notification_mailer_handle_empty_activity_description(self, browser):
        self.login(self.dossier_responsible, browser)
        self.create_task_via_browser(browser)

        # reassign task
        task = self.dossier.objectValues()[-1]
        data = {'form.widgets.transition': 'task-transition-reassign'}
        browser.open(task, data, view='assign-task')
        responsible = 'fa:{}'.format(self.secretariat_user.getId())
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(responsible)
        browser.click_on('Assign')

        mails = Mailing(self.portal).get_messages()
        self.assertEqual(len(mails), 2)
        raw_mail = mails[-1]
        self.assertIn('Reassigned from', raw_mail)

    @browsing
    def test_from_and_to_addresses(self, browser):
        self.login(self.dossier_responsible, browser)
        self.create_task_via_browser(browser)
        mail = email.message_from_string(Mailing(self.portal).pop())
        self.assertEquals('foo@example.com', mail.get('To'))
        self.assertEquals('Ziegler Robert <robert.ziegler@gever.local>', get_header(mail, 'From'))

    @browsing
    def test_task_title_is_linked_to_resolve_notification_view(self, browser):
        self.login(self.dossier_responsible, browser)
        self.create_task_via_browser(browser)
        raw_mail = Mailing(self.portal).pop()
        link = '<p><a href=3D"http://nohost/plone/@@resolve_notification?notification=\n_id=3D1">Test Task</a></p>'
        self.assertIn(link, raw_mail.strip())

    @browsing
    def test_mail_dispatcher_respects_dispatcher_roles(self, browser):
        """By default only the responsible should be notified by mail, when
        a task gets added.
        """
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier, view='++add++opengever.task.task')
        self.create_task_via_browser(browser)
        self.assertEquals(1, len(Mailing(self.portal).get_messages()))
        mail = email.message_from_string(Mailing(self.portal).pop())
        self.assertEquals('foo@example.com', get_header(mail, 'To'))

    @browsing
    def test_mail_dispatcher_respects_dispatcher_roles_even_if_its_a_group(self, browser):
        """By default only the responsible should be notified by mail, when
        a task gets added.
        """
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier, view='++add++opengever.task.task')
        self.create_task_via_browser(browser, inbox=True)
        self.assertEquals(1, len(Mailing(self.portal).get_messages()))
        mail = email.message_from_string(Mailing(self.portal).pop())
        self.assertEquals('foo@example.com', get_header(mail, 'To'))
