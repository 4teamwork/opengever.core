from ftw.testbrowser import browsing
from opengever.activity import notification_center
from opengever.activity.model import Activity
from opengever.activity.model import Notification
from opengever.activity.roles import WATCHER_ROLE
from opengever.document.activities import DocumentWatcherAddedActivity
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.versioner import Versioner
from opengever.testing import IntegrationTestCase
from zope.component import getMultiAdapter
import json


class TestDocumentChangedActivities(IntegrationTestCase):

    features = ('activity',)

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
        manager.checkin('The best version ever.')

        self.assertEqual(1, Activity.query.count())

        manager.checkout()
        manager.checkin()

        self.assertEqual(2, Activity.query.count())

        manager.revert_to_version(0)
        self.assertEqual(3, Activity.query.count())

        activities = Activity.query.all()
        self.assertEqual(3 * [u'document-version-created'],
                         [activity.kind for activity in activities])

        self.assertEqual(
            3 * [u'New document version created by B\xe4rfuss K\xe4thi (kathi.barfuss)'],
            [activity.summary for activity in activities])

        self.assertEqual(
            ['Comment: The best version ever.',
             None,
             u'Comment: Version 0 restored.'],
            [activity.description for activity in activities])

    @browsing
    def test_no_document_version_created_activity_when_cancelling_checkout(self, browser):
        self.login(self.regular_user, browser)

        versioner = Versioner(self.document)
        versioner.create_initial_version()

        self.assertEqual(0, Activity.query.count())
        manager = getMultiAdapter(
            (self.document, self.request),
            ICheckinCheckoutManager)
        manager.checkout()
        manager.cancel()

        self.assertEqual(0, Activity.query.count())

    @browsing
    def test_change_document_title_notifies_watcher(self, browser):
        self.login(self.regular_user, browser)
        notification_center().add_watcher_to_resource(
            self.document, self.meeting_user.getId(),
            WATCHER_ROLE)

        self.assertEqual(1, Notification.query.count())

        browser.open(self.document, method='PATCH',
                     data=json.dumps({u'title': u'A new title'}),
                     headers=self.api_headers)

        self.assertEqual(2, Notification.query.count())
        notification = Notification.query.all()[-1]
        self.assertEqual(u'document-title-changed', notification.activity.kind)
        self.assertEqual(self.meeting_user.getId(), notification.userid)


class TestDocumentWatcherAddedActivity(IntegrationTestCase):

    features = ('activity',)

    def setUp(self):
        super(TestDocumentWatcherAddedActivity, self).setUp()
        self.center = notification_center()

    def test_watcher_added_activity_attributes(self):
        self.login(self.regular_user)
        DocumentWatcherAddedActivity(self.document, self.request,
                                     self.meeting_user.getId()).record()
        activity = Activity.query.first()
        self.assertEqual('document-watcher-added', activity.kind)
        self.assertEqual('Added as watcher of document', activity.label)
        self.assertEqual(u'Vertr\xe4gsentwurf', activity.title)
        self.assertEqual(self.regular_user.id, activity.actor_id)
        self.assertEqual(u'Added as watcher of document by <a href="http://nohost/plone/'
                         u'@@user-details/%s">B\xe4rfuss K\xe4thi (kathi.barfuss)</a>' % self.regular_user.id,
                         activity.summary)

    def test_only_added_watcher_is_notified(self):
        self.login(self.regular_user)
        self.center.add_watcher_to_resource(self.document, self.meeting_user.getId(), WATCHER_ROLE)
        notifications = Notification.query.all()
        self.assertEqual(1, len(notifications))
        self.center.add_watcher_to_resource(self.document, self.dossier_responsible.getId(),
                                            WATCHER_ROLE)
        notifications = Notification.query.all()
        self.assertEquals(2, len(notifications))
