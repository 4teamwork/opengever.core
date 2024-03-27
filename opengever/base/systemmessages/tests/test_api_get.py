
from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.model import create_session
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import IntegrationTestCase
import pytz


class TestSystemMessagesGet(IntegrationTestCase):

    def setUp(self):
        super(TestSystemMessagesGet, self).setUp()
        self.now = datetime(2024, 3, 25, 12, 12, tzinfo=pytz.utc)

    @browsing
    def test_system_message_get_request_limited_to_manager_user(self, browser):
        self.login(self.manager, browser=browser)
        with freeze(self.now):
            browser.open(
                self.portal,
                view='@system-messages',
                method='GET',
                headers=self.api_headers
            )
        self.assertEqual(200, browser.status_code)

        self.login(self.regular_user, browser=browser)

        with freeze(self.now):
            with browser.expect_http_error(401):
                browser.open(
                    self.portal,
                    view='@system-messages',
                    method='GET',
                    headers=self.api_headers
                )
        self.assertEqual(401, browser.status_code)

    @browsing
    def test_get_system_message_by_id(self, browser):
        self.login(self.manager, browser=browser)

        with freeze(self.now):
            sys_msg = create(Builder('system-messages').having(
                admin_unit=get_current_admin_unit(),
                start=self.now)
            )
            session = create_session()
            session.add(sys_msg)
            session.flush()
        browser.open(
            self.portal,
            view='@system-messages/%s' % sys_msg.id,
            method='GET',
            headers=self.api_headers
        )
        self.assertEqual(200, browser.status_code)

        expected = {
            u'@id': u'http://nohost/plone/@system-messages/1',
            u'@type': u'virtual.ogds.systemmessages',
            u'admin_unit': u'plone',
            u'end': u'2024-03-28T12:12:00+00:00',
            u'id': 1,
            u'start': u'2024-03-25T12:12:00+00:00',
            u'text': u'English message',
            u'text_de': u'Deutsch message ',
            u'text_en': u'English message',
            u'text_fr': u'French message',
            u'type': u'info'
        }
        self.assertEqual(expected, browser.json)

    @browsing
    def test_system_messages_listing(self, browser):
        self.login(self.manager, browser=browser)
        with freeze(self.now):
            sys_msg_1 = create(Builder('system-messages'))
            sys_msg_2 = create(Builder('system-messages').having(
                admin_unit=get_current_admin_unit(),
                start=self.now,
                type="warning")
            )

            session = create_session()
            session.add(sys_msg_1)
            session.add(sys_msg_2)
            session.flush()

        browser.open(
            self.portal,
            view='@system-messages',
            method='GET',
            headers=self.api_headers
        )
        self.assertEqual(200, browser.status_code)

        expected = {
            u'@id': u'http://nohost/plone/@system-messages',
            u'items': [
                {
                    u'@id': u'http://nohost/plone/@system-messages/1',
                    u'@type': u'virtual.ogds.systemmessages',
                    u'admin_unit': None,
                    u'end': u'2024-03-28T12:12:00+00:00',
                    u'id': 1,
                    u'start': u'2024-03-25T12:12:00+00:00',
                    u'text': u'English message',
                    u'text_de': u'Deutsch message ',
                    u'text_en': u'English message',
                    u'text_fr': u'French message',
                    u'type': u'info'
                },
                {
                    u'@id': u'http://nohost/plone/@system-messages/2',
                    u'@type': u'virtual.ogds.systemmessages',
                    u'admin_unit': u'plone',
                    u'end': u'2024-03-28T12:12:00+00:00',
                    u'id': 2,
                    u'start': u'2024-03-25T12:12:00+00:00',
                    u'text': u'English message',
                    u'text_de': u'Deutsch message ',
                    u'text_en': u'English message',
                    u'text_fr': u'French message',
                    u'type': u'warning'
                }
            ]
        }

        self.assertEqual(expected, browser.json)

    @browsing
    def test_system_messages_active_filter(self, browser):
        self.login(self.manager, browser=browser)
        with freeze(self.now):
            sys_msg_1 = create(Builder('system-messages'))
            # sys_msg_2 is in active and should not be returned in the response data
            sys_msg_2 = create(Builder('system-messages').having(
                admin_unit=get_current_admin_unit(),
                start=self.now,
                type="warning",
                end=self.now - timedelta(days=4))

            )

            session = create_session()
            session.add(sys_msg_1)
            session.add(sys_msg_2)
            session.flush()

        browser.open(
            self.portal,
            view='@system-messages?active=true',
            method='GET',
            headers=self.api_headers
        )
        self.assertEqual(200, browser.status_code)

        expected = {
            u'@id': u'http://nohost/plone/@system-messages',
            u'items': [
                {
                    u'@id': u'http://nohost/plone/@system-messages/1',
                    u'@type': u'virtual.ogds.systemmessages',
                    u'admin_unit': None,
                    u'end': u'2024-03-28T12:12:00+00:00',
                    u'id': 1,
                    u'start': u'2024-03-25T12:12:00+00:00',
                    u'text': u'English message',
                    u'text_de': u'Deutsch message ',
                    u'text_en': u'English message',
                    u'text_fr': u'French message',
                    u'type': u'info'
                }
            ]
        }
        self.assertEqual(expected, browser.json)

    @browsing
    def test_system_messages_current_admin_unit_only_filter(self, browser):
        self.login(self.manager, browser=browser)
        with freeze(self.now):
            sys_msg_1 = create(Builder('system-messages'))
            # sys_msg_2 has an admin and should be only returned
            sys_msg_2 = create(Builder('system-messages').having(
                admin_unit=get_current_admin_unit(),
                start=self.now,
                type="warning",
                end=self.now - timedelta(days=4))

            )

            session = create_session()
            session.add(sys_msg_1)
            session.add(sys_msg_2)
            session.flush()

        browser.open(
            self.portal,
            view='@system-messages?current_admin_unit_only=true',
            method='GET',
            headers=self.api_headers
        )
        self.assertEqual(200, browser.status_code)

        expected = {
            u'@id': u'http://nohost/plone/@system-messages',
            u'items': [
                {
                    u'@id': u'http://nohost/plone/@system-messages/2',
                    u'@type': u'virtual.ogds.systemmessages',
                    u'admin_unit': u'plone',
                    u'end': u'2024-03-21T12:12:00+00:00',
                    u'id': 2,
                    u'start': u'2024-03-25T12:12:00+00:00',
                    u'text': u'English message',
                    u'text_de': u'Deutsch message ',
                    u'text_en': u'English message',
                    u'text_fr': u'French message',
                    u'type': u'warning'
                }
            ]
        }
        self.assertEqual(expected, browser.json)

    @browsing
    def test_language_text_full_back(self, browser):
        self.login(self.manager, browser=browser)
        with freeze(self.now):

            # create a msg with no text_de
            # Full back should take the text en
            sys_msg_1 = create(Builder('system-messages').having(
                text_de=""
            ))
            # create a message with no text_en
            # fullback should take the text_fr
            sys_msg_2 = create(Builder('system-messages').having(
                admin_unit=get_current_admin_unit(),
                text_de="",
                text_en="")
            )
        session = create_session()
        session.add(sys_msg_1)
        session.add(sys_msg_2)
        session.flush()
        browser.open(
            self.portal,
            view='@system-messages',
            method='GET',
            headers=self.api_headers
        )
        self.assertEqual(200, browser.status_code)

        expected = {
            u'@id': u'http://nohost/plone/@system-messages',
            u'items': [
                {
                    u'@id': u'http://nohost/plone/@system-messages/1',
                    u'@type': u'virtual.ogds.systemmessages',
                    u'admin_unit': None,
                    u'end': u'2024-03-28T12:12:00+00:00',
                    u'id': 1,
                    u'start': u'2024-03-25T12:12:00+00:00',
                    u'text': u'English message',
                    u'text_de': u'',
                    u'text_en': u'English message',
                    u'text_fr': u'French message',
                    u'type': u'info'
                },
                {
                    u'@id': u'http://nohost/plone/@system-messages/2',
                    u'@type': u'virtual.ogds.systemmessages',
                    u'admin_unit': u'plone',
                    u'end': u'2024-03-28T12:12:00+00:00',
                    u'id': 2,
                    u'start': u'2024-03-25T12:12:00+00:00',
                    u'text': u'French message',
                    u'text_de': u'',
                    u'text_en': u'',
                    u'text_fr': u'French message',
                    u'type': u'info'
                }
            ]
        }

        self.assertEqual(expected, browser.json)
