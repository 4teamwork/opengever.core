from datetime import date
from datetime import datetime
from DateTime import DateTime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.ogds.models.user import User
from opengever.testing import IntegrationTestCase
from Products.PlonePAS.events import UserLoggedInEvent
from zope.event import notify


class TestLastLogin(IntegrationTestCase):

    @browsing
    def test_updates_last_login_if_logged_in_event_is_fired(self, browser):
        ogds_user = User.query.get_by_userid(self.regular_user.getId())
        self.assertIsNone(ogds_user.last_login)

        self.regular_user.setMemberProperties(
            dict(login_time=DateTime('2020/02/02'), last_login_time=DateTime('2020/01/01')))
        notify(UserLoggedInEvent(self.regular_user))

        ogds_user = User.query.get_by_userid(self.regular_user.getId())

        self.assertEqual(date(2020, 2, 2), ogds_user.last_login)

    @browsing
    def test_updates_last_login_if_user_logs_in(self, browser):
        userid = self.regular_user.getId()
        ogds_user = User.query.get_by_userid(userid)
        self.assertIsNone(ogds_user.last_login)

        with freeze(datetime(2020, 2, 2, 16, 40)):
            browser.visit(view='login_form')
            browser.fill({'Login Name': userid, 'Password': 'secret'}).submit()
            ogds_user = User.query.get_by_userid(userid)
            self.assertEqual(date(2020, 2, 2), ogds_user.last_login)
