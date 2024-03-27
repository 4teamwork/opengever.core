
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.model import create_session
from opengever.testing import IntegrationTestCase
import json
import pytz


class TestSystemMessagesPatch(IntegrationTestCase):

    def setUp(self):
        super(TestSystemMessagesPatch, self).setUp()
        self.now = datetime(2024, 3, 25, 12, 12, tzinfo=pytz.utc)

    @browsing
    def test_system_message_patch_request_limited_to_manager_user(self, browser):
        self.login(self.manager, browser=browser)
        payload = {"type": "error"}
        with freeze(self.now):
            sys_msg = create(Builder('system-messages').having(
                start=self.now)
            )
            session = create_session()
            session.add(sys_msg)
            session.flush()

        browser.open(
            self.portal,
            view='@system-messages/%s' % sys_msg.id,
            data=json.dumps(payload),
            method='PATCH',
            headers=self.api_headers
        )

        self.assertEqual(200, browser.status_code)

        self.login(self.regular_user, browser=browser)

        with freeze(self.now):
            sys_msg = create(Builder('system-messages').having(start=self.now))
            session = create_session()
            session.add(sys_msg)
            session.flush()
        with browser.expect_http_error(401):
            browser.open(
                self.portal,
                view='@system-messages/%s' % sys_msg.id,
                data=json.dumps(payload),
                method='PATCH',
                headers=self.api_headers
            )

        self.assertEqual(401, browser.status_code)

    @browsing
    def test_patch_system_message(self, browser):
        self.login(self.manager, browser=browser)
        payload = {'type': 'error', 'text_en': 'The Error Msg in english'}
        with freeze(self.now):
            sys_msg = create(Builder('system-messages').having(start=self.now))
            session = create_session()
            session.add(sys_msg)
            session.flush()
        browser.open(
            self.portal,
            view='@system-messages/%s' % sys_msg.id,
            data=json.dumps(payload),
            method='PATCH',
            headers=self.api_headers
        )
        self.assertEqual(200, browser.status_code)

        expected = {
            u'@id': u'http://nohost/plone/@system-messages/1',
            u'@type': u'virtual.ogds.systemmessages',
            u'admin_unit': None,
            u'end': u'2024-03-28T12:12:00+00:00',
            u'id': 1,
            u'start': u'2024-03-25T12:12:00+00:00',
            u'text': u'The Error Msg in english',
            u'text_de': u'Deutsch message ',
            u'text_en': u'The Error Msg in english',
            u'text_fr': u'French message',
            u'type': u'error'
        }
        self.assertEqual(expected, browser.json)
