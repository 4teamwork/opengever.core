from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.utils import get_header
from ftw.testbrowser import browsing
from ftw.testing.mailing import Mailing
from opengever.activity.hooks import insert_notification_defaults
from opengever.activity.mailer import process_mail_queue
from opengever.activity.roles import TASK_RESPONSIBLE_ROLE
from opengever.base.interfaces import IOGMailSettings
from opengever.globalindex.model.task import Task
from opengever.ogds.models.user_settings import UserSettings
from opengever.task.activities import TaskAddedActivity
from opengever.testing import IntegrationTestCase
from plone import api
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

    def create_task_via_browser(self, browser, inbox=False, description=None, info_at=[]):
        browser.open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title': 'Test Task', 'Task type': 'comment'})
        if description is not None:
            browser.fill({"Text": description})
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(self.regular_user)
        if inbox:
            # XXX - How to get the correct id from the fixtured objects?
            org_unit_id = u'fa'
            inbox_id = u':'.join(('inbox', org_unit_id, ))
            form.find_widget('Issuer').fill(inbox_id)
        form.find_widget('Info at').fill(info_at)
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
            'GEVER Activity: Dossier title - Test Task', mail.get('Subject'))

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
    def test_notification_add_task_summary_is_richtext(self, browser):
        self.login(self.dossier_responsible, browser)
        self.create_task_via_browser(browser, description='Multi\nline\ncomment')
        process_mail_queue()

        mails = Mailing(self.portal).get_messages()
        self.assertEqual(len(mails), 1)
        raw_mail = mails[0]
        mail = raw_mail.decode("quopri")

        self.assertIn('<td>Multi</p>', mail)
        self.assertIn('<p>line</p>', mail)
        self.assertIn('<p>comment</td>', mail)

    @browsing
    def test_add_task_notification_mail_includes_info_at(self, browser):
        self.login(self.dossier_responsible, browser)
        self.create_task_via_browser(browser, info_at=[self.administrator.id, self.regular_user.id])
        process_mail_queue()

        mails = Mailing(self.portal).get_messages()
        self.assertEqual(len(mails), 2)
        raw_mail = mails[0]
        mail = raw_mail.decode("quopri")

        self.assertIn(
            '<tr><td valign="top" class="label">Info at</td>'
            '<td>Kohler Nicole (nicole.kohler), '
            'B\xc3\xa4rfuss K\xc3\xa4thi (kathi.barfuss)</td></tr>',
            mail)

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

        message, = Mailing(self.portal).get_mailhost().messages
        self.assertEqual(['foo@example.com'], message.mto)
        self.assertEqual('test@localhost', message.mfrom)

        mail = email.message_from_string(message.messageText)
        self.assertEquals('foo@example.com', mail.get('To'))
        self.assertEquals('Ziegler Robert <test@localhost>', get_header(mail, 'From'))
        self.assertEquals('Ziegler Robert <robert.ziegler@gever.local>', get_header(mail, 'Reply-To'))

    @browsing
    def test_from_address_with_send_with_actor_from_address_enabled(self, browser):
        api.portal.set_registry_record(
            'send_with_actor_from_address', True, IOGMailSettings)
        self.login(self.dossier_responsible, browser)

        self.create_task_via_browser(browser)
        process_mail_queue()

        mail = email.message_from_string(Mailing(self.portal).pop())
        self.assertEquals('Ziegler Robert <robert.ziegler@gever.local>', get_header(mail, 'From'))

    @browsing
    def test_from_address_fallback_if_notify_own_action_and_send_with_actor_from_address_enabled(self, browser):
        UserSettings.save_setting_for_user(
            self.regular_user.getId(), 'notify_own_actions', True)

        api.portal.set_registry_record(
            'send_with_actor_from_address', True, IOGMailSettings)

        self.login(self.dossier_responsible, browser)
        self.create_task_via_browser(browser)
        process_mail_queue()

        # It uses the email address of the currently logged in user to send
        # an email, if the recipients email is different.
        mail = email.message_from_string(Mailing(self.portal).pop())
        self.assertEquals('Ziegler Robert <robert.ziegler@gever.local>', get_header(mail, 'From'))
        self.assertEquals('foo@example.com', get_header(mail, 'To'))

        self.login(self.regular_user, browser)
        self.create_task_via_browser(browser)
        process_mail_queue()

        # But it uses the portal email address, if the senders email is the same
        # as the recipient email address. This avoids spam filters blocking the email.
        mail = email.message_from_string(Mailing(self.portal).pop())
        self.assertEquals('B\xc3\xa4rfuss K\xc3\xa4thi <test@localhost>', get_header(mail, 'From'))
        self.assertEquals('foo@example.com', get_header(mail, 'To'))

    @browsing
    def test_task_title_is_linked_to_resolve_notification_view(self, browser):
        self.login(self.dossier_responsible, browser)

        self.create_task_via_browser(browser)
        process_mail_queue()

        raw_mail = Mailing(self.portal).pop()
        link = ('<p><a href=3D"http://nohost/plone/@@resolve_notification?notificati=\non_id=3D1">'
                'Vertr=C3=A4ge mit der kantonalen Finanzverwaltung - Test Task</a=\n></p>')
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


class TestAlternativeNotificationEmail(IntegrationTestCase):

    def setUp(self):
        super(TestAlternativeNotificationEmail, self).setUp()
        self.portal.email_from_address = 'test@localhost'
        self.login(self.regular_user)
        api.portal.set_registry_record(
            'alternative_notification_email_enabled', True, IOGMailSettings)
        UserSettings.get_or_create(self.regular_user.id).notification_email = u'private@example.org'

    def test_recipient_changes_but_sender_and_reply_to_use_identity_address(self):
        from opengever.activity.mail import PloneNotificationMailer
        mailer = PloneNotificationMailer()
        mailer.prepare_html = lambda data: u'Notification'
        msg, mail_to, mail_from = mailer.prepare_mail(
            to_userid=self.regular_user.id, from_userid=self.dossier_responsible.id)
        self.assertEqual('private@example.org', mail_to)
        self.assertEqual('private@example.org', msg['To'])
        self.assertEqual('test@localhost', mail_from)
        self.assertIn('robert.ziegler@gever.local', msg['Reply-To'].encode())

    def test_sender_policy_with_feature_enabled_and_disabled(self):
        from opengever.activity.mail import PloneNotificationMailer
        mailer = PloneNotificationMailer()
        mailer.prepare_html = lambda data: u'Notification'
        recipient = self.get_ogds_user(self.regular_user)
        for enabled in [False, True]:
            api.portal.set_registry_record(
                'alternative_notification_email_enabled', enabled, IOGMailSettings)
            for actor_from in [False, True]:
                api.portal.set_registry_record(
                    'send_with_actor_from_address', actor_from, IOGMailSettings)
                for actor_id in [self.regular_user.id, self.dossier_responsible.id]:
                    actor = self.get_ogds_user(
                        self.regular_user if actor_id == self.regular_user.id
                        else self.dossier_responsible)
                    msg, mail_to, mail_from = mailer.prepare_mail(
                        to_userid=recipient.userid, from_userid=actor_id)
                    self.assertEqual(
                        'private@example.org' if enabled else recipient.email, mail_to)
                    if actor_from and actor_id != recipient.userid:
                        self.assertEqual(actor.email, mail_from)
                        self.assertIsNone(msg['Reply-To'])
                    else:
                        self.assertEqual('test@localhost', mail_from)
                        self.assertIn(actor.email, msg['Reply-To'].encode())

    def test_self_notification_uses_userid_with_actor_from_enabled(self):
        from opengever.activity.mail import PloneNotificationMailer
        api.portal.set_registry_record('send_with_actor_from_address', True, IOGMailSettings)
        mailer = PloneNotificationMailer()
        mailer.prepare_html = lambda data: u'Notification'
        msg, mail_to, mail_from = mailer.prepare_mail(
            to_userid=self.regular_user.id, from_userid=self.regular_user.id)
        self.assertEqual('private@example.org', mail_to)
        self.assertEqual('test@localhost', mail_from)
        self.assertIn('foo@example.com', msg['Reply-To'].encode())

    def test_distinct_users_with_same_primary_keep_sender_policy(self):
        from opengever.activity.mail import PloneNotificationMailer
        actor = self.get_ogds_user(self.dossier_responsible)
        actor.email = self.get_ogds_user(self.regular_user).email
        api.portal.set_registry_record('send_with_actor_from_address', True, IOGMailSettings)
        mailer = PloneNotificationMailer()
        mailer.prepare_html = lambda data: u'Notification'
        for enabled in [False, True]:
            api.portal.set_registry_record(
                'alternative_notification_email_enabled', enabled, IOGMailSettings)
            msg, mail_to, mail_from = mailer.prepare_mail(
                to_userid=self.regular_user.id, from_userid=self.dossier_responsible.id)
            self.assertEqual('test@localhost', mail_from)
            self.assertIn('test@localhost', msg['From'].encode())
            self.assertIn(actor.email, msg['Reply-To'].encode())

    def test_actor_without_primary_uses_deployment_sender_without_reply_to(self):
        from opengever.activity.mail import PloneNotificationMailer
        actor = self.get_ogds_user(self.regular_user)
        mailer = PloneNotificationMailer()
        mailer.prepare_html = lambda data: u'Notification'
        for primary in [None, '', '  ']:
            actor.email = primary
            for actor_from in [False, True]:
                api.portal.set_registry_record('send_with_actor_from_address', actor_from, IOGMailSettings)
                for recipient_id in [self.regular_user.id, self.dossier_responsible.id]:
                    msg, mail_to, mail_from = mailer.prepare_mail(
                        to_userid=recipient_id, from_userid=self.regular_user.id)
                    self.assertEqual('test@localhost', mail_from)
                    self.assertIn('test@localhost', msg['From'].encode())
                    self.assertNotIn('private@example.org', msg['From'].encode())
                    self.assertIsNone(msg['Reply-To'])
                    if recipient_id == self.regular_user.id:
                        self.assertEqual('private@example.org', mail_to)

    def test_direct_email_callers_keep_their_address(self):

        from opengever.activity.mail import PloneNotificationMailer
        mailer = PloneNotificationMailer()
        mailer.prepare_html = lambda data: u'Notification'
        msg, mail_to, mail_from = mailer.prepare_mail(
            to_email='direct@example.org', from_userid=self.regular_user.id)
        self.assertEqual('direct@example.org', mail_to)

    def test_missing_user_is_not_queued(self):
        from mock import patch
        from opengever.activity.mail import PloneNotificationMailer
        mailer = PloneNotificationMailer()
        mailer.prepare_html = lambda data: u'Notification'
        with patch('opengever.activity.mailer.mail_queue.put') as queue:
            msg, mail_to, mail_from = mailer.prepare_mail(to_userid='missing-user')
            mailer.send_mail(msg, mail_to, mail_from)
            self.assertFalse(queue.called)

    def test_dispatch_presence_check_uses_alternative_without_primary(self):
        from mock import Mock
        from mock import patch
        from opengever.activity.mail import PloneNotificationMailer
        self.get_ogds_user(self.regular_user).email = None
        notification = Mock(userid=self.regular_user.id)
        mailer = PloneNotificationMailer()
        mailer.get_data = lambda notification: {}
        mailer.prepare_html = lambda data: u'Notification'
        notification.activity.actor_id = None
        with patch.object(mailer, 'send_mail') as send:
            mailer.dispatch_notification(notification)
            self.assertEqual('private@example.org', send.call_args[0][1])
