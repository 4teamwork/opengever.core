from datetime import datetime
from email import message_from_string
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from ftw.testing.mailing import Mailing
from opengever.activity.digest import DigestMailer
from opengever.activity.model import Digest
from opengever.testing import IntegrationTestCase
import pytz


class TestDigestMail(IntegrationTestCase):

    def setUp(self):
        super(TestDigestMail, self).setUp()
        Mailing(self.portal).set_up()

        resource = create(Builder('resource').oguid('fd:123'))
        activity = create(
            Builder('activity')
            .having(title=u'Bitte \xc4nderungen nachvollziehen',
                    created=pytz.UTC.localize(datetime(2017, 10, 15, 18, 24)),
                    resource=resource))

        self.note1 = create(Builder('notification')
                            .having(activity=activity,
                                    is_digest=True,
                                    userid=self.regular_user.getId()))
        self.note2 = create(Builder('notification')
                            .having(activity=activity,
                                    is_digest=True,
                                    userid=self.dossier_responsible.getId()))

    def tearDown(self):
        super(TestDigestMail, self).tearDown()
        Mailing(self.portal).tear_down()

    def test_sends_mail_to_all_notified_users(self):
        DigestMailer().send_digests()

        messages = [message_from_string(mail)
                    for mail in Mailing(self.portal).get_messages()]
        self.assertEquals(2, len(messages))
        self.assertEquals(['foo@example.com', 'robert.ziegler@gever.local'],
                          [message.get('To') for message in messages])

    def test_sends_only_not_yet_sended_notifications(self):
        self.note2.sent_in_digest = True

        DigestMailer().send_digests()

        messages = [message_from_string(mail)
                    for mail in Mailing(self.portal).get_messages()]
        self.assertEquals(1, len(messages))
        self.assertEquals(['foo@example.com'],
                          [message.get('To') for message in messages])

    @browsing
    def test_mail_contains_date_activity_summaries(self, browser):
        with freeze(datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)):
            DigestMailer().send_digests()

        messages = [message_from_string(mail)
                    for mail in Mailing(self.portal).get_messages()]

        browser.open_html(str(messages[0].get_payload()[0]))

        self.assertEquals('Oct 16, 201= 7', browser.css('table p').text[0])
        self.assertEquals(['Daily Digest for B=C3=A4rfuss K=C3=A4thi'],
                          browser.css('h1').text)
        self.assertEquals(['Bitte =C3=84nderungen nachvollzie= hen'],
                          browser.css('h2 a').text)

    def test_send_in_digest_flag_is_enabled_after_send(self):
        DigestMailer().send_digests()

        self.assertTrue(self.note1.sent_in_digest)
        self.assertTrue(self.note2.sent_in_digest)

    def test_record_all_dispatches_in_the_digest_table(self):
        now = datetime(2017, 10, 16, 0, 0, tzinfo=pytz.utc)
        with freeze(now):
            DigestMailer().send_digests()

        self.assertEquals(
            [now, now],
            [digest.last_dispatch for digest in Digest.query.all()])
        self.assertEquals(
            [self.regular_user.getId(), self.dossier_responsible.getId()],
            [digest.userid for digest in Digest.query.all()])

    def test_only_send_digest_when_interval_has_been_expired(self):
        create(Builder('digest')
               .having(userid=self.regular_user.getId(),
                       last_dispatch=datetime(2017, 10, 15, 12, 30, tzinfo=pytz.utc)))

        create(Builder('digest')
               .having(userid=self.dossier_responsible.getId(),
                       last_dispatch=datetime(2017, 10, 16, 9, tzinfo=pytz.utc)))

        with freeze(datetime(2017, 10, 16, 14, 30, tzinfo=pytz.utc)):
            DigestMailer().send_digests()

            messages = [message_from_string(mail)
                        for mail in Mailing(self.portal).get_messages()]

            self.assertEquals(1, len(messages))
            self.assertEquals('foo@example.com', messages[0].get('To'))

    def test_interval_tolerance(self):
        create(Builder('digest')
               .having(userid=self.regular_user.getId(),
                       last_dispatch=datetime(2017, 10, 15, 12, 30, tzinfo=pytz.utc)))

        create(Builder('digest')
               .having(userid=self.dossier_responsible.getId(),
                       last_dispatch=datetime(2017, 10, 16, 9, tzinfo=pytz.utc)))

        # test interval expired because of tolerance
        Mailing(self.portal).reset()
        with freeze(datetime(2017, 10, 16, 11, 30, tzinfo=pytz.utc)):
            DigestMailer().send_digests()

            messages = [message_from_string(mail)
                        for mail in Mailing(self.portal).get_messages()]

            self.assertEquals(1, len(messages))
            self.assertEquals('foo@example.com', messages[0].get('To'))
