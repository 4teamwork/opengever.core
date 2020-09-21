from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.api.testing import RelativeSession
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ZSERVER_TESTING
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from opengever.wopi.lock import create_lock as create_wopi_lock
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.protect import createToken
from zope.app.intid.interfaces import IIntIds
from zope.component import getMultiAdapter
from zope.component import getUtility
import transaction


class TestDocumentStatus(IntegrationTestCase):

    @browsing
    def test_document_status_for_mails(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.mail_eml, view='status', headers=self.api_headers)
        expected = {
            u'checked_out': False,
            u'checked_out_by': None,
            u'checked_out_collaboratively': False,
            u'int_id': getUtility(IIntIds).getId(self.mail_eml),
            u'locked': False,
            u'locked_by': None,
            u'title': u'Die B\xfcrgschaft',
        }
        self.assertEqual(expected, browser.json)


class TestBaseDocumentApi(FunctionalTestCase):
    """Test plone.rest endpoints on base documents."""

    layer = OPENGEVER_FUNCTIONAL_ZSERVER_TESTING

    def setUp(self):
        super(TestBaseDocumentApi, self).setUp()

        # Set up the requests wrapper
        self.portal = self.layer['portal']
        self.api = RelativeSession(self.portal.absolute_url())
        self.api.headers.update({'Accept': 'application/json'})
        self.api.auth = (TEST_USER_NAME, TEST_USER_PASSWORD)

        # Set up a minimal GEVER site
        self.repo = create(Builder('repository_root'))
        self.repofolder = create(Builder('repository').within(self.repo))
        self.dossier = create(Builder('dossier').within(self.repofolder))
        self.document = create(Builder('document').within(self.dossier))

    def test_document_status_json(self):
        site_id = api.portal.get().id
        path_segments = [s for s in self.document.getPhysicalPath()
                         if s != site_id]
        document_path = '/'.join(path_segments)
        response = self.api.get(document_path + '/status').json()

        self.assertIn('int_id', response)
        self.assertEqual(
            getUtility(IIntIds).getId(self.document), response['int_id'])

        self.assertIn('title', response)
        self.assertEqual(self.document.title_or_id(), response['title'])

        self.assertIn('checked_out', response)
        self.assertEqual(False, response['checked_out'])

        self.assertIn('checked_out_collaboratively', response)
        self.assertEqual(False, response['checked_out_collaboratively'])

        self.assertIn('checked_out_by', response)
        self.assertEqual(None, response['checked_out_by'])

        self.assertIn('locked', response)
        self.assertEqual(False, response['locked'])

        self.assertIn('locked_by', response)
        self.assertEqual(None, response['locked_by'])

        # Check out the document
        self.api.headers.update({'Accept': 'text/html'})
        self.api.get(
            document_path
            + '/@@checkout_documents'
            + '?_authenticator={}'.format(createToken())
            )

        self.api.headers.update({'Accept': 'application/json'})
        response = self.api.get(document_path + '/status').json()

        self.assertIn('checked_out', response)
        self.assertEqual(True, response['checked_out'])

        self.assertIn('checked_out_by', response)
        self.assertEqual(TEST_USER_ID, response['checked_out_by'])

        # Lock the document
        self.api.headers.update({
            'Content-Type': 'text/xml; charset="utf-8"',
            'Timeout': 'Infinite, Second-4100000000',
            'Depth': '0',
        })

        body = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<D:lockinfo xmlns:D="DAV:">\n'
            '  <D:lockscope><D:exclusive/></D:lockscope>\n'
            '  <D:locktype><D:write/></D:locktype>\n'
            '  <D:owner>\n'
            '  <D:href>Office Connector</D:href>\n'
            '  </D:owner>\n'
            '</D:lockinfo>'
        )

        self.api.headers.update({'Accept': 'text/html'})
        self.api.request(
            'LOCK',
            document_path,
            data=body,
            )

        self.api.headers.update({'Accept': 'application/json'})
        response = self.api.get(document_path + '/status').json()

        self.assertIn('locked', response)
        self.assertEqual(True, response['locked'])

        self.assertIn('locked_by', response)
        self.assertEqual(TEST_USER_ID, response['locked_by'])

    def test_document_status_api_returns_info_about_collaborative_checkouts(self):
        manager = getMultiAdapter((self.document, self.document.REQUEST),
                                  ICheckinCheckoutManager)
        manager.checkout(collaborative=True)
        create_wopi_lock(self.document, 'my-token')
        transaction.commit()

        site_id = api.portal.get().id
        path_segments = [s for s in self.document.getPhysicalPath()
                         if s != site_id]
        document_path = '/'.join(path_segments)
        response = self.api.get(document_path + '/status').json()

        self.assertIn('checked_out', response)
        self.assertEqual(True, response['checked_out'])

        self.assertIn('checked_out_collaboratively', response)
        self.assertEqual(True, response['checked_out_collaboratively'])

        self.assertIn('checked_out_by', response)
        self.assertEqual(TEST_USER_ID, response['checked_out_by'])

        self.assertIn('locked', response)
        self.assertEqual(True, response['locked'])

        self.assertIn('locked_by', response)
        self.assertEqual(TEST_USER_ID, response['locked_by'])
