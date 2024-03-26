from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.model import create_session
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import IntegrationTestCase
from plone import api
import pytz


class TestSystemMessagesGet(IntegrationTestCase):

    def setUp(self):
        super(TestSystemMessagesGet, self).setUp()
        self.now = datetime(2024, 3, 25, 12, 12, tzinfo=pytz.utc)
        self.lang_tool = api.portal.get_tool('portal_languages')
        self.lang_tool.supported_langs = ['de-ch', 'fr-ch', 'en-us']

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
                start_ts=self.now)
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
            u'@type': u'virtual.ogds.systemmessage',
            u'admin_unit': u'plone',
            u'end_ts': u'2024-03-28T12:12:00+00:00',
            u'id': 1,
            u'start_ts': u'2024-03-25T12:12:00+00:00',
            u'text': u'English message',
            u'text_de': u'Deutsch message ',
            u'text_en': u'English message',
            u'text_fr': u'French message',
            u'type': u'info',
            u'active': False
        }
        self.assertEqual(expected, browser.json)

    @browsing
    def test_system_messages_listing(self, browser):
        self.login(self.manager, browser=browser)
        with freeze(self.now):
            sys_msg_1 = create(Builder('system-messages'))
            sys_msg_2 = create(Builder('system-messages').having(
                admin_unit=get_current_admin_unit(),
                start_ts=self.now,
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
                    u'@type': u'virtual.ogds.systemmessage',
                    u'admin_unit': None,
                    u'end_ts': u'2024-03-28T12:12:00+00:00',
                    u'id': 1,
                    u'start_ts': u'2024-03-25T12:12:00+00:00',
                    u'text': u'English message',
                    u'text_de': u'Deutsch message ',
                    u'text_en': u'English message',
                    u'text_fr': u'French message',
                    u'type': u'info',
                    u'active': False
                },
                {
                    u'@id': u'http://nohost/plone/@system-messages/2',
                    u'@type': u'virtual.ogds.systemmessage',
                    u'admin_unit': u'plone',
                    u'end_ts': u'2024-03-28T12:12:00+00:00',
                    u'id': 2,
                    u'start_ts': u'2024-03-25T12:12:00+00:00',
                    u'text': u'English message',
                    u'text_de': u'Deutsch message ',
                    u'text_en': u'English message',
                    u'text_fr': u'French message',
                    u'type': u'warning',
                    u'active': False
                }
            ]
        }

        self.assertEqual(expected, browser.json)

    @browsing
    def test_system_messages_active_filter(self, browser):
        self.login(self.manager, browser=browser)
        with freeze(self.now):
            sys_msg_1 = create(Builder('system-messages'))
            sys_msg_2 = create(Builder('system-messages'))

            sys_msg_3 = create(Builder('system-messages').having(
                start_ts=self.now - timedelta(days=6),
                end_ts=self.now - timedelta(days=3),
                type="warning"
            ))

            session = create_session()
            session.add(sys_msg_1)
            session.add(sys_msg_2)
            session.add(sys_msg_3)
            session.flush()

            browser.open(
                self.portal,
                view='@system-messages?filters.active:record:boolean=True',
                method='GET',
                headers=self.api_headers
            )
            self.assertEqual(200, browser.status_code)

        expected = {
            u'@id': u'http://nohost/plone/@system-messages',
            u'items': [
                {
                    u'@id': u'http://nohost/plone/@system-messages/1',
                    u'@type': u'virtual.ogds.systemmessage',
                    u'admin_unit': None,
                    u'end_ts': u'2024-03-28T12:12:00+00:00',
                    u'id': 1,
                    u'start_ts': u'2024-03-25T12:12:00+00:00',
                    u'text': u'English message',
                    u'text_de': u'Deutsch message ',
                    u'text_en': u'English message',
                    u'text_fr': u'French message',
                    u'type': u'info',
                    u'active': True
                },
                {
                    u'@id': u'http://nohost/plone/@system-messages/2',
                    u'@type': u'virtual.ogds.systemmessage',
                    u'admin_unit': None,
                    u'end_ts': u'2024-03-28T12:12:00+00:00',
                    u'id': 2,
                    u'start_ts': u'2024-03-25T12:12:00+00:00',
                    u'text': u'English message',
                    u'text_de': u'Deutsch message ',
                    u'text_en': u'English message',
                    u'text_fr': u'French message',
                    u'type': u'info',
                    u'active': True
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
                start_ts=self.now,
                type="warning",
                end_ts=self.now - timedelta(days=4))

            )

            session = create_session()
            session.add(sys_msg_1)
            session.add(sys_msg_2)
            session.flush()

        browser.open(
            self.portal,
            view='@system-messages?filters.current_admin_unit_only:record:boolean=True',
            method='GET',
            headers=self.api_headers
        )
        self.assertEqual(200, browser.status_code)
        expected = {
            u'@id': u'http://nohost/plone/@system-messages',
            u'items': [
                {
                    u'@id': u'http://nohost/plone/@system-messages/2',
                    u'@type': u'virtual.ogds.systemmessage',
                    u'admin_unit': u'plone',
                    u'end_ts': u'2024-03-21T12:12:00+00:00',
                    u'id': 2,
                    u'start_ts': u'2024-03-25T12:12:00+00:00',
                    u'text': u'English message',
                    u'text_de': u'Deutsch message ',
                    u'text_en': u'English message',
                    u'text_fr': u'French message',
                    u'type': u'warning',
                    u'active': False
                }
            ]
        }
        self.assertEqual(expected, browser.json)

    @browsing
    def test_text_prefered_language_english(self, browser):
        self.login(self.manager, browser=browser)

        with freeze(self.now):
            self.lang_tool.setDefaultLanguage('en')
            sys_msg = create(Builder('system-messages'))

        session = create_session()
        session.add(sys_msg)

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
                    u'@type': u'virtual.ogds.systemmessage',
                    u'admin_unit': None,
                    u'end_ts': u'2024-03-28T12:12:00+00:00',
                    u'id': 1,
                    u'start_ts': u'2024-03-25T12:12:00+00:00',
                    u'text': u'English message',
                    u'text_de': u'Deutsch message ',
                    u'text_en': u'English message',
                    u'text_fr': u'French message',
                    u'type': u'info',
                    u'active': False
                }
            ]
        }
        self.assertEqual(expected, browser.json)

    @browsing
    def test_text_prefered_language_french(self, browser):
        self.login(self.manager, browser=browser)

        with freeze(self.now):
            self.lang_tool.setDefaultLanguage('fr')
            sys_msg = create(Builder('system-messages'))

        session = create_session()
        session.add(sys_msg)

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
                    u'@type': u'virtual.ogds.systemmessage',
                    u'admin_unit': None,
                    u'end_ts': u'2024-03-28T12:12:00+00:00',
                    u'id': 1,
                    u'start_ts': u'2024-03-25T12:12:00+00:00',
                    u'text': u'French message',
                    u'text_de': u'Deutsch message ',
                    u'text_en': u'English message',
                    u'text_fr': u'French message',
                    u'type': u'info',
                    u'active': False
                }
            ]
        }
        self.assertEqual(expected, browser.json)

    @browsing
    def test_text_prefered_language_german(self, browser):
        self.login(self.manager, browser=browser)

        with freeze(self.now):
            self.lang_tool.setDefaultLanguage('de')
            sys_msg = create(Builder('system-messages'))

        session = create_session()
        session.add(sys_msg)

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
                    u'@type': u'virtual.ogds.systemmessage',
                    u'admin_unit': None,
                    u'end_ts': u'2024-03-28T12:12:00+00:00',
                    u'id': 1,
                    u'start_ts': u'2024-03-25T12:12:00+00:00',
                    u'text': u'Deutsch message ',
                    u'text_de': u'Deutsch message ',
                    u'text_en': u'English message',
                    u'text_fr': u'French message',
                    u'type': u'info',
                    u'active': False
                }
            ]
        }
        self.assertEqual(expected, browser.json)

    @browsing
    def test_text_fallback_language_german(self, browser):
        self.login(self.manager, browser=browser)

        with freeze(self.now):
            self.lang_tool.setDefaultLanguage('de')

            # no German and no English text so French text will be displayed
            sys_msg_1 = create(Builder('system-messages').having(
                text_de="",
                text_en="")
            )

            # no German but French as fallback text will be displayed
            sys_msg_2 = create(Builder('system-messages').having(
                text_de="",)
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
                    u'@type': u'virtual.ogds.systemmessage',
                    u'admin_unit': None,
                    u'end_ts': u'2024-03-28T12:12:00+00:00',
                    u'id': 1,
                    u'start_ts': u'2024-03-25T12:12:00+00:00',
                    u'text': u'French message',
                    u'text_de': u'',
                    u'text_en': u'',
                    u'text_fr': u'French message',
                    u'type': u'info',
                    u'active': False
                },
                {
                    u'@id': u'http://nohost/plone/@system-messages/2',
                    u'@type': u'virtual.ogds.systemmessage',
                    u'admin_unit': None,
                    u'end_ts': u'2024-03-28T12:12:00+00:00',
                    u'id': 2,
                    u'start_ts': u'2024-03-25T12:12:00+00:00',
                    u'text': u'French message',
                    u'text_de': u'',
                    u'text_en': u'English message',
                    u'text_fr': u'French message',
                    u'type': u'info',
                    u'active': False
                },

            ]
        }

        self.assertEqual(expected, browser.json)

    @browsing
    def test_text_fallback_language_french(self, browser):
        self.login(self.manager, browser=browser)

        with freeze(self.now):
            self.lang_tool.setDefaultLanguage('fr')

            # no French but German text so German will be will be displayed
            sys_msg_1 = create(Builder('system-messages').having(
                text_fr="")
            )
            # no French and no German text so English will be will be displayed
            sys_msg_2 = create(Builder('system-messages').having(
                text_de="",
                text_fr="")
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
                    u'@type': u'virtual.ogds.systemmessage',
                    u'admin_unit': None,
                    u'end_ts': u'2024-03-28T12:12:00+00:00',
                    u'id': 1,
                    u'start_ts': u'2024-03-25T12:12:00+00:00',
                    u'text': u'Deutsch message ',
                    u'text_de': u'Deutsch message ',
                    u'text_en': u'English message',
                    u'text_fr': u'',
                    u'type': u'info',
                    u'active': False
                },
                {
                    u'@id': u'http://nohost/plone/@system-messages/2',
                    u'@type': u'virtual.ogds.systemmessage',
                    u'admin_unit': None,
                    u'end_ts': u'2024-03-28T12:12:00+00:00',
                    u'id': 2,
                    u'start_ts': u'2024-03-25T12:12:00+00:00',
                    u'text': u'English message',
                    u'text_de': u'',
                    u'text_en': u'English message',
                    u'text_fr': u'',
                    u'type': u'info',
                    u'active': False
                },

            ]
        }

        self.assertEqual(expected, browser.json)
