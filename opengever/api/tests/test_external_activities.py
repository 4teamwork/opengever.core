from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from mock import patch
from opengever.activity.model import Activity
from opengever.activity.notification_settings import NotificationSettings
from opengever.activity.roles import ALWAYS
from opengever.ogds.models.service import ogds_service
from opengever.testing import IntegrationTestCase
from plone import api
import json


class TestExternalActivitiesPost(IntegrationTestCase):

    features = ("activity",)

    @browsing
    def test_creating_external_activity_requires_authentication(self, browser):
        url = "%s/@external-activities" % self.portal.absolute_url()
        with browser.expect_http_error(code=401):
            browser.open(
                url,
                method="POST",
                data=json.dumps({}),
                headers=self.api_headers,
            )

    @browsing
    def test_can_create_new_external_activity(self, browser):
        self.login(self.regular_user, browser=browser)

        url = "%s/@external-activities" % self.portal.absolute_url()

        activity_data = {
            "notification_recipients": [self.regular_user.id],
            "resource_url": "https://igdev.onegovgever.ch/intergever/outbox",
            "title": {
                "de": "Technische Quittung f\xc3\xbcr eCH-0147 Export",
                "en": "Transfer report for eCH-0147 export",
            },
            "label": {
                "de": "eCH-0147 Quittung erhalten",
                "en": "Received eCH-0147 report",
            },
            "summary": {
                "de": "Technische Quittung f\xc3\xbcr eCH-0147 Export erhalten",
                "en": "Received transfer report for eCH-0147 export",
            },
            "description": {
                "de": 'Technische Quittung f\xc3\xbcr eCH-0147 Export "Mein Dossier" erhalten',
                "en": 'Received transfer report for eCH-0147 export "Mein Dossier"',
            },
        }
        with freeze(datetime(2019, 12, 31, 17, 45)):
            browser.open(
                url,
                method="POST",
                data=json.dumps(activity_data),
                headers=self.api_headers,
            )

        self.assertEqual(201, browser.status_code)

        activity = Activity.query.all()[-1]

        self.assertIsNone(activity.resource)
        self.assertEqual("external-activity", activity.kind)
        self.assertEqual(
            u'Received transfer report for eCH-0147 export "Mein Dossier"',
            activity.description,
        )

        self.assertEqual(
            {
                "actor_id": "__system__",
                "actor_label": u"",
                "created": u"2019-12-31T17:45:00+00:00",
                "label": u"Received eCH-0147 report",
                "summary": u"Received transfer report for eCH-0147 export",
                "title": u"Transfer report for eCH-0147 export",
            },
            activity.serialize(),
        )

        notifications = activity.notifications
        self.assertEqual(1, len(notifications))
        self.assertEqual(
            {
                "@id": "http://nohost/plone/@notifications/%s/1" % self.regular_user.id,
                "actor_id": "__system__",
                "actor_label": u"",
                "created": u"2019-12-31T17:45:00+00:00",
                "label": u"Received eCH-0147 report",
                "link": "http://nohost/plone/@@resolve_notification?notification_id=1",
                "notification_id": 1,
                "oguid": None,
                "read": False,
                "summary": u"Received transfer report for eCH-0147 export",
                "title": u"Transfer report for eCH-0147 export",
            },
            notifications[0].serialize(self.portal.absolute_url()),
        )

    @browsing
    def test_regular_user_can_only_create_external_activity_for_themselves(self, browser):
        self.login(self.regular_user, browser=browser)

        url = "%s/@external-activities" % self.portal.absolute_url()

        activity_data = {
            "notification_recipients": ["someone.else"],
        }
        with browser.expect_http_error(code=401):
            browser.open(
                url,
                method="POST",
                data=json.dumps(activity_data),
                headers=self.api_headers,
            )

        self.assertEqual({
            u'type': u'Unauthorized',
            u'message': u'Insufficient privileges to create external '
                        u'activities with notification recipients other '
                        u'than yourself.',
        }, browser.json)

    @browsing
    def test_privileged_user_may_create_activities_for_other_users(self, browser):
        self.login(self.regular_user, browser=browser)
        api.user.grant_roles(
            user=self.regular_user,
            roles=['PrivilegedNotificationDispatcher'],
        )

        url = "%s/@external-activities" % self.portal.absolute_url()

        activity_data = {
            "notification_recipients": [self.dossier_responsible.id],
            "title": {"en": "Foo"},
            "label": {"en": "Foo"},
            "description": {"en": "Foo"},
            "summary": {"en": "Foo"},
            "resource_url": "http://example.org",
        }
        browser.open(
            url,
            method="POST",
            data=json.dumps(activity_data),
            headers=self.api_headers,
        )

        activity = Activity.query.all()[-1]
        self.assertDictContainsSubset({
            u'actor_id': u'__system__',
            u'actor_label': u'',
            u'label': u"Foo",
            u'summary': u"Foo",
            u'title': u"Foo",
            }, activity.serialize()
        )

        self.assertEqual(
            self.dossier_responsible.id,
            activity.notifications[0].userid,
        )

    @browsing
    def test_notification_recipients_accepts_and_resolves_groups(self, browser):
        self.login(self.regular_user, browser=browser)
        api.user.grant_roles(
            user=self.regular_user,
            roles=['PrivilegedNotificationDispatcher'],
        )

        group = ogds_service().fetch_group('fa_users')
        self.assertTrue(len(group.users) > 1)

        url = "%s/@external-activities" % self.portal.absolute_url()

        activity_data = {
            "notification_recipients": [group.groupid],
            "title": {"en": "Foo"},
            "label": {"en": "Foo"},
            "description": {"en": "Foo"},
            "summary": {"en": "Foo"},
            "resource_url": "http://example.org",
        }
        browser.open(
            url,
            method="POST",
            data=json.dumps(activity_data),
            headers=self.api_headers,
        )

        activity = Activity.query.all()[-1]
        self.assertItemsEqual(
            [user.userid for user in group.users if user.active],
            [notification.userid for notification in activity.notifications],
        )

    @browsing
    def test_avoids_duplicate_notifications(self, browser):
        self.login(self.regular_user, browser=browser)
        api.user.grant_roles(
            user=self.regular_user,
            roles=['PrivilegedNotificationDispatcher'],
        )

        group = ogds_service().fetch_group('fa_users')
        duplicate_recipient = ogds_service().fetch_user(self.dossier_responsible.id)
        self.assertIn(duplicate_recipient, group.users)

        url = "%s/@external-activities" % self.portal.absolute_url()

        activity_data = {
            "notification_recipients": [
                group.groupid,
                duplicate_recipient.userid,
                duplicate_recipient.userid,
            ],
            "title": {"en": "Foo"},
            "label": {"en": "Foo"},
            "description": {"en": "Foo"},
            "summary": {"en": "Foo"},
            "resource_url": "http://example.org",
        }
        browser.open(
            url,
            method="POST",
            data=json.dumps(activity_data),
            headers=self.api_headers,
        )

        activity = Activity.query.all()[-1]
        notified_userids = [n.userid for n in activity.notifications]
        self.assertEqual(1, notified_userids.count(duplicate_recipient.userid))

    @browsing
    def test_creating_external_activity_with_incomplete_schema_fails(self, browser):
        self.login(self.regular_user, browser=browser)

        url = "%s/@external-activities" % self.portal.absolute_url()

        activity_data = {
            "notification_recipients": [self.regular_user.id],
        }

        with browser.expect_http_error(code=400, reason="Bad Request"):
            browser.open(
                url,
                method="POST",
                data=json.dumps(activity_data),
                headers=self.api_headers,
            )

        self.assertEqual({
            u'type': u'BadRequest',
            u'message': u"[('resource_url', RequiredMissing('resource_url')), "
                        u"('title', RequiredMissing('title')), "
                        u"('label', RequiredMissing('label')), "
                        u"('summary', RequiredMissing('summary')), "
                        u"('description', RequiredMissing('description'))]",
        }, browser.json)

    @browsing
    def test_creating_external_activity_validates_schema_fields(self, browser):
        self.login(self.regular_user, browser=browser)

        url = "%s/@external-activities" % self.portal.absolute_url()

        activity_data = {
            "notification_recipients": [self.regular_user.id],
            "resource_url": 42,
            "title": {
                "not-a-lang": "Foo",
            },
            "label": 42,
            "summary": {
                "de": 42
            },
            "description": ['a', 'b', 'c']
        }

        with browser.expect_http_error(code=400, reason="Bad Request"):
            browser.open(
                url,
                method="POST",
                data=json.dumps(activity_data),
                headers=self.api_headers,
            )

        self.assertIn(
            "('resource_url', WrongType(42, <type 'str'>, 'resource_url'))",
            browser.json["message"]
        )

        self.assertIn(
            "('title', WrongContainedType([ConstraintNotSatisfied(u'not-a-lang')], 'title'))",
            browser.json["message"],
        )

        self.assertIn(
            "('label', WrongType(42, <type 'dict'>, 'label'))",
            browser.json["message"],
        )

        self.assertIn(
            "('summary', WrongContainedType([WrongType(42, <type 'unicode'>, '')], 'summary'))",
            browser.json["message"],
        )

        self.assertIn(
            "('description', WrongType([u'a', u'b', u'c'], <type 'dict'>, 'description'))",
            browser.json["message"],
        )

    @patch('opengever.activity.mail.PloneNotificationMailer.dispatch_notification')
    @browsing
    def test_error_handling_for_dispatch_failures(self, patched_dispatch, browser):
        self.login(self.regular_user, browser=browser)
        api.user.grant_roles(
            user=self.regular_user,
            roles=['PrivilegedNotificationDispatcher'],
        )

        def fail_for_david(notification):
            if notification.userid == self.member_admin.getId():
                raise Exception('Boom')

        patched_dispatch.side_effect = fail_for_david

        defaults = NotificationSettings()._get_default_notification_settings()
        defaults.get('external-activity').mail_notification_roles = [ALWAYS]

        group = ogds_service().fetch_group('fa_users')
        self.assertTrue(len(group.users) > 1)

        url = "%s/@external-activities" % self.portal.absolute_url()

        activity_data = {
            "notification_recipients": [group.groupid],
            "title": {"en": "Foo"},
            "label": {"en": "Foo"},
            "description": {"en": "Foo"},
            "summary": {"en": "Foo"},
            "resource_url": "http://example.org",
        }
        browser.open(
            url,
            method="POST",
            data=json.dumps(activity_data),
            headers=self.api_headers,
        )

        self.assertEqual([{
            'type': 'dispatch_failed',
            'msg': u"Failed to dispatch notification for user u'%s'" % self.member_admin.getId(),
            'userid': self.member_admin.getId(),
        }], browser.json['errors'])

        activity = Activity.query.all()[-1]

        self.assertItemsEqual(
            [user.userid for user in group.users if user.active],
            [notification.userid for notification in activity.notifications],
        )

    @browsing
    def test_error_handling_for_actor_lookup_failure(self, browser):
        self.login(self.regular_user, browser=browser)
        api.user.grant_roles(
            user=self.regular_user,
            roles=['PrivilegedNotificationDispatcher'],
        )

        url = "%s/@external-activities" % self.portal.absolute_url()

        activity_data = {
            "notification_recipients": ['user.that.doesnt.exist'],
            "title": {"en": "Foo"},
            "label": {"en": "Foo"},
            "description": {"en": "Foo"},
            "summary": {"en": "Foo"},
            "resource_url": "http://example.org",
        }
        browser.open(
            url,
            method="POST",
            data=json.dumps(activity_data),
            headers=self.api_headers,
        )

        self.assertEqual([{
            u'type': u'unresolvable_actor_id',
            u'msg': u"Could not resolve Actor ID 'user.that.doesnt.exist' to a group or user",
            u'actor_id': u'user.that.doesnt.exist',
            }], browser.json['errors'])
