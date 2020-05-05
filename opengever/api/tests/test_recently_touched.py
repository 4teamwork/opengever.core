from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.base.interfaces import IRecentlyTouchedSettings
from opengever.base.touched import ObjectTouchedEvent
from opengever.base.touched import RECENTLY_TOUCHED_KEY
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.dossier.tests.test_resolve import ResolveTestHelper
from opengever.testing import IntegrationTestCase
from plone import api
from zope.annotation import IAnnotations
from zope.component import queryMultiAdapter
from zope.event import notify


class TestRecentlyModifiedGet(IntegrationTestCase, ResolveTestHelper):

    def _clear_recently_touched_log(self, user_id):
        del IAnnotations(self.portal)[RECENTLY_TOUCHED_KEY][user_id][:]

    @browsing
    def test_lists_recently_modified_objs_for_given_user(self, browser):
        self.login(self.regular_user, browser=browser)

        self._clear_recently_touched_log(self.regular_user.getId())

        with freeze(datetime(2018, 4, 30)):
            notify(ObjectTouchedEvent(self.document))

        url = '%s/@recently-touched/%s' % (
            self.portal.absolute_url(), self.regular_user.getId())
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.assertEquals(
            {'checked_out': [],
             'recently_touched': [{
                 'icon_class': 'icon-docx',
                 'is_leafnode': None,
                 'description': u'Wichtige Vertr\xe4ge',
                 # Because of an incorrect timezone handling in the freezer
                 # last_touched should be `2018-04-30T00:00:00+02:00`
                 'last_touched': '2018-04-30T02:00:00+02:00',
                 'title': u'Vertr\xe4gsentwurf',
                 'review_state': 'document-state-draft',
                 '@id': self.document.absolute_url(),
                 '@type': 'opengever.document.document'}]},
            browser.json)

    @browsing
    def test_lists_checked_out_docs_for_given_user(self, browser):
        self.login(self.regular_user, browser=browser)

        self._clear_recently_touched_log(self.regular_user.getId())

        with freeze(datetime(2018, 4, 30)):
            manager = queryMultiAdapter(
                (self.document, self.request), ICheckinCheckoutManager)
            manager.checkout()

        url = '%s/@recently-touched/%s' % (
            self.portal.absolute_url(), self.regular_user.getId())
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.assertEquals(
            {'checked_out': [{
                'icon_class': 'icon-docx is-checked-out-by-current-user',
                'is_leafnode': None,
                'description': u'Wichtige Vertr\xe4ge',
                'last_touched': '2018-04-30T00:00:00+02:00',
                'title': u'Vertr\xe4gsentwurf',
                'review_state': 'document-state-draft',
                '@id': self.document.absolute_url(),
                '@type': 'opengever.document.document'}],
             'recently_touched': []},
            browser.json)

    @browsing
    def test_respects_metadata_fields_parameter(self, browser):
        self.login(self.regular_user, browser=browser)

        self._clear_recently_touched_log(self.regular_user.getId())

        with freeze(datetime(2018, 4, 30)):
            manager = queryMultiAdapter(
                (self.document, self.request), ICheckinCheckoutManager)
            manager.checkout()

        url = '%s/@recently-touched/%s?metadata_fields:list=checked_out&metadata_fields:list=filename' % (
            self.portal.absolute_url(), self.regular_user.getId())
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.assertEquals(
            {'checked_out': [{
                'icon_class': 'icon-docx is-checked-out-by-current-user',
                'is_leafnode': None,
                'description': u'Wichtige Vertr\xe4ge',
                'checked_out': self.regular_user.id,
                'filename': 'Vertraegsentwurf.docx',
                # Because of an incorrect timezone handling in the freezer
                # last_touched should be `2018-04-30T00:00:00+02:00`
                'last_touched': '2018-04-30T00:00:00+02:00',
                'title': u'Vertr\xe4gsentwurf',
                'review_state': 'document-state-draft',
                '@id': self.document.absolute_url(),
                '@type': 'opengever.document.document'}],
             'recently_touched': []},
            browser.json)

    @browsing
    def test_lists_docs_checked_out_by_other_user_correctly(self, browser):
        self.login(self.regular_user, browser=browser)

        self._clear_recently_touched_log(self.regular_user.getId())

        with freeze(datetime(2018, 4, 30)):
            manager = queryMultiAdapter(
                (self.document, self.request), ICheckinCheckoutManager)
            manager.checkout()
            manager.checkin()

        with self.login(self.secretariat_user, browser=browser):
            manager = queryMultiAdapter(
                (self.document, self.request), ICheckinCheckoutManager)
            manager.checkout()

        url = '%s/@recently-touched/%s' % (
            self.portal.absolute_url(), self.regular_user.getId())
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.assertEquals(
            {'checked_out': [],
             'recently_touched': [{
                 'icon_class': 'icon-docx is-checked-out',
                 'is_leafnode': None,
                 'description': u'Wichtige Vertr\xe4ge',
                 # Because of an incorrect timezone handling in the freezer
                 # last_touched should be `2018-04-30T00:00:00+02:00`
                 'last_touched': '2018-04-30T02:00:00+02:00',
                 'title': u'Vertr\xe4gsentwurf',
                 'review_state': 'document-state-draft',
                 '@id': self.document.absolute_url(),
                 '@type': 'opengever.document.document'}]},
            browser.json)

    @browsing
    def test_checked_out_docs_arent_listed_twice(self, browser):
        self.login(self.regular_user, browser=browser)

        self._clear_recently_touched_log(self.regular_user.getId())

        with freeze(datetime(2018, 4, 30)):
            manager = queryMultiAdapter(
                (self.document, self.request), ICheckinCheckoutManager)
            manager.checkout()
            notify(ObjectTouchedEvent(self.document))

        url = '%s/@recently-touched/%s' % (
            self.portal.absolute_url(), self.regular_user.getId())
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        # If a document is both in the log for recently touched objects as
        # well as checked out, it must only be listed once, in the
        # checked out documents section.

        self.assertEqual(200, browser.status_code)
        self.assertEquals(
            {'checked_out': [{
                'icon_class': 'icon-docx is-checked-out-by-current-user',
                'is_leafnode': None,
                'description': u'Wichtige Vertr\xe4ge',
                'last_touched': '2018-04-30T00:00:00+02:00',
                'title': u'Vertr\xe4gsentwurf',
                'review_state': 'document-state-draft',
                '@id': self.document.absolute_url(),
                '@type': 'opengever.document.document'}],
             'recently_touched': []},
            browser.json)

    @browsing
    def test_journal_and_task_pdfs_are_not_listed(self, browser):
        self.activate_feature('tasks-pdf')
        self.activate_feature('journal-pdf')
        self.login(self.secretariat_user, browser)

        create(Builder('task')
               .within(self.empty_dossier)
               .titled(u'Arbeitsentwurf checken')
               .having(responsible_client='fa',
                       responsible=self.secretariat_user.getId(),
                       issuer=self.dossier_responsible.getId(),
                       task_type='correction',
                       deadline=date(2016, 11, 1))
               .in_state('task-state-tested-and-closed'))

        with freeze(datetime(2018, 4, 30)):
            self.resolve(self.empty_dossier, browser)

        url = '%s/@recently-touched/%s' % (
            self.portal.absolute_url(), self.secretariat_user.getId())
        browser.open(url, method='GET', headers={'Accept': 'application/json'})

        self.assertEqual(200, browser.status_code)
        self.assertEquals(
            {'checked_out': [],
             'recently_touched': []},
            browser.json)

    @browsing
    def test_limits_recently_touched_items(self, browser):
        self.login(self.regular_user, browser=browser)
        user_id = self.regular_user.getId()

        self._clear_recently_touched_log(user_id)

        # Touch a couple documents (more than the current limit)
        docs = [self.document, self.private_document, self.expired_document,
                self.subdocument, self.taskdocument]

        with freeze(datetime(2018, 4, 30)) as freezer:
            for doc in docs:
                freezer.forward(minutes=1)
                notify(ObjectTouchedEvent(doc))

        api.portal.set_registry_record(
            'limit', 3, IRecentlyTouchedSettings)

        url = '%s/@recently-touched/%s' % (
            self.portal.absolute_url(), self.regular_user.getId())
        browser.open(
            url, method='GET', headers={'Accept': 'application/json'})

        # Even though the storage contains more logged touched entries, the
        # API endpoint should truncate them to the currently defined limit.

        self.assertEqual(200, browser.status_code)
        recently_touched_list = browser.json['recently_touched']
        self.assertEqual(3, len(recently_touched_list))

    @browsing
    def test_rejects_request_for_other_user(self, browser):
        self.login(self.regular_user, browser=browser)

        url = '%s/@recently-touched/%s' % (
            self.portal.absolute_url(), 'other-user')
        with browser.expect_unauthorized():
            browser.open(
                url, method='GET', headers={'Accept': 'application/json'})
        self.assertEqual(401, browser.status_code)

    @browsing
    def test_raises_when_userid_is_missing(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(400):
            url = '%s/@recently-touched' % self.portal.absolute_url()
            browser.open(url, method='GET',
                         headers={'Accept': 'application/json'})

        self.assertEqual(
            {'type': 'BadRequest',
             'message': 'Must supply user ID as path parameter'},
            browser.json)
