from ftw.testbrowser import browsing
from opengever.activity import notification_center
from opengever.activity.model import Activity
from opengever.activity.model import Notification
from opengever.activity.roles import WATCHER_ROLE
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import IntegrationTestCase
from zope.component import getMultiAdapter
import json


class TestDocumentChangedActivities(IntegrationTestCase):

    features = ('activity', 'document-watchers')

    @browsing
    def test_document_title_changed_activity(self, browser):
        self.login(self.regular_user, browser)
        self.assertEqual(0, Activity.query.count())

        browser.open(self.document, method='PATCH',
                     data=json.dumps({u'title': u'A new title'}),
                     headers=self.api_headers)

        self.assertEqual(1, Activity.query.count())
        activity = Activity.query.first()
        self.assertEqual(u'document-title-changed', activity.kind)
        self.assertEquals(u'Title changed by B\xe4rfuss K\xe4thi (kathi.barfuss)', activity.summary)

    @browsing
    def test_document_title_changed_whitout_watchers_feature_enabled(self, browser):
        self.deactivate_feature('document-watchers')
        self.login(self.regular_user, browser)
        self.assertEqual(0, Activity.query.count())

        browser.open(self.document, method='PATCH',
                     data=json.dumps({u'title': u'A new title'}),
                     headers=self.api_headers)

        self.assertEqual(0, Activity.query.count())

    @browsing
    def test_mail_title_changed_activity(self, browser):
        self.login(self.regular_user, browser)
        self.assertEqual(0, Activity.query.count())

        browser.open(self.mail_eml, method='PATCH',
                     data=json.dumps({u'title': u'A new title'}),
                     headers=self.api_headers)

        self.assertEqual(1, Activity.query.count())
        activity = Activity.query.first()
        self.assertEqual(u'document-title-changed', activity.kind)
        self.assertEquals(u'Title changed by B\xe4rfuss K\xe4thi (kathi.barfuss)', activity.summary)

    @browsing
    def test_document_author_changed_activity(self, browser):
        self.login(self.regular_user, browser)
        self.assertEqual(0, Activity.query.count())

        browser.open(self.document, method='PATCH',
                     data=json.dumps({u'document_author': u'James Bond'}),
                     headers=self.api_headers)

        self.assertEqual(1, Activity.query.count())
        activity = Activity.query.first()
        self.assertEqual(u'document-author-changed', activity.kind)
        self.assertEquals(
            u'Author changed by B\xe4rfuss K\xe4thi (kathi.barfuss)', activity.summary)

    @browsing
    def test_mail_author_changed_activity(self, browser):
        self.login(self.regular_user, browser)
        self.assertEqual(0, Activity.query.count())

        browser.open(self.mail_eml, method='PATCH',
                     data=json.dumps({u'document_author': u'James Bond'}),
                     headers=self.api_headers)

        self.assertEqual(1, Activity.query.count())
        activity = Activity.query.first()
        self.assertEqual(u'document-author-changed', activity.kind)
        self.assertEquals(
            u'Author changed by B\xe4rfuss K\xe4thi (kathi.barfuss)', activity.summary)

    @browsing
    def test_document_version_created_activity(self, browser):
        self.login(self.regular_user, browser)
        self.assertEqual(0, Activity.query.count())
        manager = getMultiAdapter(
            (self.document, self.request),
            ICheckinCheckoutManager)
        manager.checkout()
        manager.checkin()

        self.assertEqual(1, Activity.query.count())
        manager.revert_to_version(0)
        self.assertEqual(2, Activity.query.count())

        activities = Activity.query.all()
        self.assertEqual([u'document-version-created', u'document-version-created'],
                         [activity.kind for activity in activities])

        self.assertEqual([u'New document version created by B\xe4rfuss K\xe4thi (kathi.barfuss)',
                          u'New document version created by B\xe4rfuss K\xe4thi (kathi.barfuss)'],
                         [activity.summary for activity in activities])

    @browsing
    def test_change_document_title_notifies_watcher(self, browser):
        self.login(self.regular_user, browser)
        notification_center().add_watcher_to_resource(
            self.document, self.meeting_user.getId(),
            WATCHER_ROLE)

        self.assertEqual(0, Notification.query.count())

        browser.open(self.document, method='PATCH',
                     data=json.dumps({u'title': u'A new title'}),
                     headers=self.api_headers)

        self.assertEqual(1, Notification.query.count())
        notification = Notification.query.first()
        self.assertEqual(u'document-title-changed', notification.activity.kind)
        self.assertEqual(self.meeting_user.getId(), notification.userid)
