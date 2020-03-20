from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.utils import get_header
from ftw.testbrowser import browsing
from ftw.testing.mailing import Mailing
from opengever.activity.hooks import insert_notification_defaults
from opengever.activity.mailer import process_mail_queue
from opengever.activity.roles import TASK_RESPONSIBLE_ROLE
from opengever.globalindex.model.task import Task
from opengever.task.activities import TaskAddedActivity
from opengever.testing import IntegrationTestCase
from zope.globalrequest import getRequest
import email
import transaction


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

    def create_task_via_browser(self, browser, inbox=False, description=None):
        browser.open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title': 'Test Task', 'Task Type': 'comment'})
        if description is not None:
            browser.fill({"Text": description})
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.regular_user)
        if inbox:
            # XXX - How to get the correct id from the fixtured objects?
            org_unit_id = u'fa'
            inbox_id = u':'.join(('inbox', org_unit_id, ))
            form.find_widget('Issuer').fill(inbox_id)
        browser.css('#form-buttons-save').first.click()

    @browsing
    def test_subject_is_title(self, browser):
        self.login(self.dossier_responsible, browser)

        # We change the dossier title to ASCII-only, makes it easier
        # to test the mail subject
        self.dossier.title = "Dossier title"

        self.create_task_via_browser(browser)
        process_mail_queue()

        mail = email.message_from_string(Mailing(self.portal).pop())

        self.assertEquals(
            'GEVER Activity: [Dossier title] Test Task', mail.get('Subject'))

    @browsing
    def test_notification_summary_is_split_into_paragraphs(self, browser):
        self.login(self.dossier_responsible, browser)
        self.create_task_via_browser(browser)
        process_mail_queue()

        # Discard the first mail
        Mailing(self.portal).pop()

        # XXX - did not find a neater way to get the task quickly
        browser.open(Task.query.all()[-1], view='addcommentresponse')
        browser.fill({'Response': 'Multi\n\nline\ncomment'})
        browser.css('#form-buttons-save').first.click()
        process_mail_queue()

        mails = Mailing(self.portal).get_messages()
        self.assertEqual(len(mails), 1)
        raw_mail = mails[0]

        self.assertIn('<p>Multi</p>', raw_mail)
        self.assertIn('<p></p>', raw_mail)
        self.assertIn('<p>line</p>', raw_mail)
        self.assertIn('<p>comment</p>', raw_mail)

    @browsing
    def test_notification_add_task_summary_is_split_into_lines(self, browser):
        self.login(self.dossier_responsible, browser)
        self.create_task_via_browser(browser, description='Multi\nline\ncomment')
        process_mail_queue()

        mails = Mailing(self.portal).get_messages()
        self.assertEqual(len(mails), 1)
        raw_mail = mails[0]
        mail = raw_mail.decode("quopri")

        self.assertIn('<td>Multi<br />', mail)
        self.assertIn('line<br />', mail)
        self.assertIn('comment</td>', mail)

    @browsing
    def test_notification_mailer_handle_empty_activity_description(self, browser):
        self.login(self.dossier_responsible, browser)
        self.create_task_via_browser(browser)
        process_mail_queue()

        # Discard the first mail
        Mailing(self.portal).pop()

        # reassign task
        task = self.dossier.objectValues()[-1]
        data = {'form.widgets.transition': 'task-transition-reassign'}
        browser.open(task, data, view='assign-task')
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.secretariat_user)
        browser.click_on('Assign')
        process_mail_queue()

        mails = Mailing(self.portal).get_messages()
        mails.sort(key=lambda data: email.message_from_string(data).get('To'))

        self.assertEqual(len(mails), 1)
        raw_mail = mails[0]
        self.assertIn('Reassigned from', raw_mail)

    @browsing
    def test_from_and_to_addresses(self, browser):
        self.login(self.dossier_responsible, browser)

        self.create_task_via_browser(browser)
        process_mail_queue()

        mail = email.message_from_string(Mailing(self.portal).pop())
        self.assertEquals('foo@example.com', mail.get('To'))
        self.assertEquals('OneGov GEVER <test@localhost>', get_header(mail, 'From'))

    @browsing
    def test_task_title_is_linked_to_resolve_notification_view(self, browser):
        self.login(self.dossier_responsible, browser)

        self.create_task_via_browser(browser)
        process_mail_queue()

        raw_mail = Mailing(self.portal).pop()
        link = ('<p><a href=3D"http://nohost/plone/@@resolve_notification?notificati=\non_id=3D1">'
                '[Vertr=C3=A4ge mit der kantonalen...] Test Task</a></p>')
        self.assertIn(link, raw_mail.strip())

    @browsing
    def test_mail_dispatcher_respects_dispatcher_roles(self, browser):
        """By default only the responsible should be notified by mail, when
        a task gets added.
        """
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier, view='++add++opengever.task.task')
        self.create_task_via_browser(browser)
        process_mail_queue()

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
        process_mail_queue()

        self.assertEquals(1, len(Mailing(self.portal).get_messages()))
        mail = email.message_from_string(Mailing(self.portal).pop())
        self.assertEquals('foo@example.com', get_header(mail, 'To'))


class TestNotificationMailsAndSavepoints(IntegrationTestCase):

    features = (
        'activity',
    )

    def setUp(self):
        # Overridden - don't perform IntegrationTestCase's usual setup,
        # because that would replace the MailHost with a mock. We need the
        # real one's data manager though to reproduce the issue with the
        # test below
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.deactivate_extjs()
        map(self.parse_feature, self.features)
        if 'activity' in self.features:
            insert_notification_defaults(self.portal)

        task_responsible = self.regular_user
        create(Builder('watcher').having(actorid=task_responsible.id))

        # Make sure mails to responsible are enabled for task added
        create(Builder('notification_setting')
               .having(kind='task-added',
                       userid=task_responsible.id,
                       mail_notification_roles=[TASK_RESPONSIBLE_ROLE],
                       badge_notification_roles=[],
                       digest_notification_roles=[]))

    def tearDown(self):
        # Overridden - don't attempt to tear down Mailing helper
        super(IntegrationTestCase, self).tearDown()

    def test_notification_mails_dont_interfere_with_txn_savepoints(self):
        # Login with a different user than task_responsible to trigger mail
        self.login(self.dossier_responsible)

        # Trigger a notification that dispatches a mail
        activity = TaskAddedActivity(self.task, getRequest())
        activity.record()

        # Creating a savepoint will fail with the MailDataManager if it's
        # already registered as a transaction manager at that point
        transaction.savepoint()
