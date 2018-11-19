from datetime import datetime
from ftw.testbrowser import restapi
from ftw.testing import freeze
from opengever.base.interfaces import IRecentlyTouchedSettings
from opengever.base.touched import ObjectTouchedEvent
from opengever.base.touched import RECENTLY_TOUCHED_KEY
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import IntegrationTestCase
from plone import api
from zope.annotation import IAnnotations
from zope.component import queryMultiAdapter
from zope.event import notify


class TestRecentlyModifiedGet(IntegrationTestCase):

    def _clear_recently_touched_log(self, user_id):
        del IAnnotations(self.portal)[RECENTLY_TOUCHED_KEY][user_id][:]

    @restapi
    def test_lists_recently_modified_objs_for_given_user(self, api_client):
        self.login(self.regular_user, api_client)
        self._clear_recently_touched_log(self.regular_user.getId())

        with freeze(datetime(2018, 4, 30)):
            notify(ObjectTouchedEvent(self.document))

        endpoint = '@recently-touched/%s' % self.regular_user.getId()
        api_client.open(endpoint=endpoint)

        self.assertEqual(200, api_client.status_code)
        expected_item = {
            'checked_out': [],
            'recently_touched': [{
                'icon_class': 'icon-docx',
                'last_touched': '2018-04-30T00:00:00',
                'target_url': self.document.absolute_url(),
                'title': u'Vertr\xe4gsentwurf',
            }],
        }
        self.assertEquals(expected_item, api_client.contents)

    @restapi
    def test_lists_checked_out_docs_for_given_user(self, api_client):
        self.login(self.regular_user, api_client)
        self._clear_recently_touched_log(self.regular_user.getId())

        with freeze(datetime(2018, 4, 30)):
            manager = queryMultiAdapter((self.document, self.request), ICheckinCheckoutManager)
            manager.checkout()

        endpoint = '@recently-touched/%s' % self.regular_user.getId()
        api_client.open(endpoint=endpoint)

        self.assertEqual(200, api_client.status_code)
        expected_item = {
            'checked_out': [{
                'icon_class': 'icon-docx is-checked-out-by-current-user',
                'last_touched': '2018-04-30T00:00:00+02:00',
                'target_url': self.document.absolute_url(),
                'title': u'Vertr\xe4gsentwurf',
            }],
            'recently_touched': [],
        }
        self.assertEquals(expected_item, api_client.contents)

    @restapi
    def test_checked_out_docs_arent_listed_twice(self, api_client):
        self.login(self.regular_user, api_client)
        self._clear_recently_touched_log(self.regular_user.getId())

        with freeze(datetime(2018, 4, 30)):
            manager = queryMultiAdapter((self.document, self.request), ICheckinCheckoutManager)
            manager.checkout()
            notify(ObjectTouchedEvent(self.document))

        endpoint = '@recently-touched/%s' % self.regular_user.getId()
        api_client.open(endpoint=endpoint)

        # If a document is both in the log for recently touched objects as
        # well as checked out, it must only be listed once, in the
        # checked out documents section.

        self.assertEqual(200, api_client.status_code)
        expected_item = {
            'checked_out': [{
                'icon_class': 'icon-docx is-checked-out-by-current-user',
                'last_touched': '2018-04-30T00:00:00+02:00',
                'target_url': self.document.absolute_url(),
                'title': u'Vertr\xe4gsentwurf',
            }],
            'recently_touched': [],
        }
        self.assertEquals(expected_item, api_client.contents)

    @restapi
    def test_limits_recently_touched_items(self, api_client):
        self.login(self.regular_user, api_client)
        user_id = self.regular_user.getId()
        self._clear_recently_touched_log(user_id)

        # Touch a couple documents (more than the current limit)
        docs = [self.document, self.private_document, self.expired_document, self.subdocument, self.taskdocument]

        with freeze(datetime(2018, 4, 30)) as freezer:
            for doc in docs:
                freezer.forward(minutes=1)
                notify(ObjectTouchedEvent(doc))

        api.portal.set_registry_record('limit', 3, IRecentlyTouchedSettings)

        endpoint = '@recently-touched/%s' % self.regular_user.getId()
        api_client.open(endpoint=endpoint)

        # Even though the storage contains more logged touched entries, the
        # API endpoint should truncate them to the currently defined limit.

        self.assertEqual(200, api_client.status_code)
        recently_touched_list = api_client.contents['recently_touched']
        self.assertEqual(3, len(recently_touched_list))

    @restapi
    def test_rejects_request_for_other_user(self, api_client):
        self.login(self.regular_user, api_client)
        with api_client.expect_unauthorized():
            api_client.open(endpoint='@recently-touched/other-user')
        self.assertEqual(401, api_client.status_code)

    @restapi
    def test_raises_when_userid_is_missing(self, api_client):
        self.login(self.regular_user, api_client)
        with api_client.expect_http_error(400):
            api_client.open(endpoint='@recently-touched')

        expected_error = {
            'type': 'BadRequest',
            'message': 'Must supply user ID as path parameter',
        }
        self.assertEqual(expected_error, api_client.contents)
