from datetime import datetime
from datetime import timedelta
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.testing import IntegrationTestCase
import json
import pytz


class TestSystemMessagesPost(IntegrationTestCase):

    def setUp(self):
        super(TestSystemMessagesPost, self).setUp()
        self.now = datetime(2024, 3, 25, 12, 12, tzinfo=pytz.utc)
        self.payload = self.create_test_payload()

    def create_test_payload(self):
        payload = {
            "admin_unit": get_current_admin_unit().unit_id,
            "text_en": "EN",
            "text_de": "DE",
            "text_fr": "FR",
            "start_ts": self.now.isoformat(),
            "end_ts": (self.now + timedelta(days=3)).isoformat(),
            "type": "info"
        }
        return payload

    @browsing
    def test_system_message_post_request_limited_to_manager_user(self, browser):
        self.login(self.manager, browser=browser)
        with freeze(self.now):
            browser.open(self.portal, view='@system-messages', method='POST',
                         data=json.dumps(self.payload),
                         headers=self.api_headers)
        self.assertEqual(201, browser.status_code)

        self.login(self.regular_user, browser=browser)

        with freeze(self.now):
            with browser.expect_http_error(401):
                browser.open(
                    self.portal,
                    view='@system-messages',
                    method='POST',
                    data=json.dumps(self.payload),
                    headers=self.api_headers
                )
        self.assertEqual(401, browser.status_code)

    @browsing
    def test_valid_post_system_message(self, browser):
        self.login(self.manager, browser=browser)

        with freeze(self.now):
            browser.open(
                self.portal,
                view='@system-messages',
                method='POST',
                data=json.dumps(self.payload),
                headers=self.api_headers
            )
            self.assertEqual(201, browser.status_code)

            expected = {
                u'@id': u'http://nohost/plone/@system-messages/1',
                u'@type': u'virtual.ogds.systemmessage',
                u'id': 1,
                u'admin_unit': get_current_admin_unit().unit_id,
                u'text_en': u'EN',
                u'text_de': u'DE',
                u'text_fr': u'FR',
                u'text': u'EN',
                u'start_ts': u'2024-03-25T12:12:00+00:00',
                u'end_ts': u'2024-03-28T12:12:00+00:00',
                u'type': u'info',
                u'active': True
            }
            self.assertEqual(expected, browser.json)

    @browsing
    def test_valid_post_system_message_with_no_admin_unit(self, browser):
        self.login(self.manager, browser=browser)
        self.payload.update({"admin_unit": None})

        with freeze(self.now):
            browser.open(
                self.portal,
                view='@system-messages',
                method='POST',
                data=json.dumps(self.payload),
                headers=self.api_headers
            )
            self.assertEqual(201, browser.status_code)

            expected = {
                u'@id': u'http://nohost/plone/@system-messages/1',
                u'@type': u'virtual.ogds.systemmessage',
                u'id': 1,
                u'admin_unit': None,
                u'text_en': u'EN',
                u'text_de': u'DE',
                u'text_fr': u'FR',
                u'text': u'EN',
                u'start_ts': u'2024-03-25T12:12:00+00:00',
                u'end_ts': u'2024-03-28T12:12:00+00:00',
                u'type': u'info',
                u'active': True
            }
            self.assertEqual(expected, browser.json)

    @browsing
    def test_invalid_post_system_message_due_to_missing_type(self, browser):
        self.login(self.manager, browser=browser)

        # Modify the type in place so we can send empty system message type
        self.payload.update({"type": ""})

        with freeze(self.now):
            with browser.expect_http_error(400):
                browser.open(
                    self.portal,
                    view='@system-messages',
                    method='POST',
                    data=json.dumps(self.payload),
                    headers=self.api_headers
                )
            self.assertEqual(400, browser.status_code)

            expected = {
                u'additional_metadata': {
                    u"fields": [{
                        u"field": u"type",
                        u"translated_message": u"Constraint not satisfied",
                        u"type": u"ConstraintNotSatisfied"
                    }]
                },

                u'message': u"[{'field': 'type', 'message': u'Constraint not satisfied', 'error': 'ConstraintNotSatisfied'}]",  # noqa: E501
                u'translated_message': u'Inputs not valid',
                u'type': u'BadRequest'
            }

            self.assertDictContainsSubset(expected, browser.json)

            # Assert that 'traceback' key exists in the response.json if the user is logged in as a manager
            self.assertIn("traceback", browser.json.keys())

    @browsing
    def test_invalid_post_system_message_due_to_unsupported_type(self, browser):
        self.login(self.manager, browser=browser)

        # Modify the type in place so we can send empty system message type
        self.payload.update({"type": "critical"})

        with freeze(self.now):
            with browser.expect_http_error(400):
                browser.open(
                    self.portal,
                    view='@system-messages',
                    method='POST',
                    data=json.dumps(self.payload),
                    headers=self.api_headers
                )
            self.assertEqual(400, browser.status_code)

            expected = {
                u'additional_metadata': {
                    u'fields': [
                        {
                            u'field': u'type',
                            u'translated_message': u'Constraint not satisfied',
                            u'type': u'ConstraintNotSatisfied'
                        }
                    ]
                },
                u'message': u"[{'field': 'type', 'message': u'Constraint not satisfied', 'error': 'ConstraintNotSatisfied'}]",  # noqa: E501
                u'translated_message': u'Inputs not valid',
                u'type': u'BadRequest'
            }

            self.assertDictContainsSubset(expected, browser.json)

            # Assert that 'traceback' key exists in the response.json if the user is logged in as a manager
            self.assertIn("traceback", browser.json.keys())

    @browsing
    def test_invalid_post_system_message_due_to_end_date_smaller_than_start(self, browser):
        self.login(self.manager, browser=browser)

        # Modify the type in place so we can modify the end date
        self.payload.update({"end_ts": (self.now - timedelta(days=3)).isoformat(), })

        with freeze(self.now):
            with browser.expect_http_error(400):
                browser.open(
                    self.portal,
                    view='@system-messages',
                    method='POST',
                    data=json.dumps(self.payload),
                    headers=self.api_headers
                )
            self.assertEqual(400, browser.status_code)

            expected = {
                u'additional_metadata': {},
                u'message': u"[{'field': None, 'message': 'The message end date must be bigger than the start date', 'error': 'InvalidEndDate'}]",  # noqa: E501
                u'translated_message': u'The message end date must be bigger than the start date',
                u'type': u'BadRequest'
            }

            self.assertDictContainsSubset(expected, browser.json)

            # Assert that 'traceback' key exists in the response.json if the user is logged in as a manager
            self.assertIn("traceback", browser.json.keys())
