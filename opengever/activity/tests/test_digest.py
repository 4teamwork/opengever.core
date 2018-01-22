from datetime import datetime
from email import message_from_string
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from ftw.testing.mailing import Mailing
from opengever.activity.digest import DigestMailer
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

        create(Builder('notification')
               .having(activity=activity,
                       is_digest=True,
                       userid=self.regular_user.getId()))
        create(Builder('notification')
               .having(activity=activity,
                       is_digest=True,
                       userid=self.dossier_responsible.getId()))

    def tearDown(self):
        super(TestDigestMail, self).tearDown()
        Mailing(self.portal).tear_down()

    def test_sends_mail_to_all_notified_users(self):
        with freeze(datetime(2017, 10, 16, 0, 0)):
            DigestMailer().send_digests()

        messages = [message_from_string(mail)
                    for mail in Mailing(self.portal).get_messages()]
        self.assertEquals(2, len(messages))
        self.assertEquals(['foo@example.com', 'robert.ziegler@gever.local'],
                          [message.get('To') for message in messages])

    @browsing
    def test_mail_contains_date_activity_summaries(self, browser):
        with freeze(datetime(2017, 10, 16, 0, 0)):
            DigestMailer().send_digests()

        messages = [message_from_string(mail)
                    for mail in Mailing(self.portal).get_messages()]

        browser.open_html(str(messages[0].get_payload()[0]))

        self.assertEquals('O= ct 16, 2017', browser.css('table p').text[0])
        self.assertEquals(['Daily Digest'], browser.css('h1').text)
        self.assertEquals(['Bitte =C3=84nderungen nachvollziehen'],
                          browser.css('h2 a').text)
