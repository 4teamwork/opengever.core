from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.model import create_session
from opengever.base.systemmessages.models import SystemMessage
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import IntegrationTestCase
import pytz


class TestSystemMessagesDelete(IntegrationTestCase):

    def setUp(self):
        super(TestSystemMessagesDelete, self).setUp()
        self.now = datetime(2024, 3, 25, 12, 12, tzinfo=pytz.utc)

    @browsing
    def test_system_message_delete_request_limited_to_manager_user(self, browser):

        self.login(self.regular_user, browser=browser)

        with freeze(self.now):
            sys_msg = create(Builder('system-messages').having(
                admin_unit=get_current_admin_unit(),
                start_ts=self.now)
            )
            session = create_session()
            session.add(sys_msg)
            session.flush()
            with browser.expect_http_error(401):
                browser.open(
                    self.portal,
                    view='@system-messages/%s' % sys_msg.id,
                    method='DELETE',
                    headers=self.api_headers
                )
        self.assertEqual(401, browser.status_code)

    @browsing
    def test_delete_system_message(self, browser):
        self.login(self.manager, browser=browser)
        with freeze(self.now):
            sys_msg = create(Builder('system-messages').having(
                admin_unit=get_current_admin_unit(),
                start_ts=self.now)
            )
            session = create_session()
            session.add(sys_msg)
            session.flush()

        self.assertEqual(1, SystemMessage.query.count())
        browser.open(
            self.portal,
            view='@system-messages/%s' % sys_msg.id,
            method='DELETE',
            headers=self.api_headers
        )
        self.assertEqual(204, browser.status_code)
        self.assertEqual('', browser.contents)
        self.assertEqual(0, SystemMessage.query.count())
