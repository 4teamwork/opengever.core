from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.officeconnector.testing import JWT_SIGNING_SECRET_PLONE
from opengever.testing import IntegrationTestCase
import jwt


class TestOCCheckoutRedirect(IntegrationTestCase):

    @browsing
    def test_oc_checkout_redirects_to_oc_checkout_url(self, browser):
        self.login(self.regular_user, browser)

        with freeze(datetime(2022, 11, 17)):
            browser.allow_redirects = False
            browser.open(self.document, view='@@oc_checkout')

            self.assertEqual(302, browser.status_code)

            oc_url = browser.headers['location']
            raw_token = oc_url.split(':')[-1]
            token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))

        expected_token = {
            u'action': u'checkout',
            u'documents': [u'createtreatydossiers000000000002'],
            u'exp': 1668686400,
            u'sub': self.regular_user.id,
            u'url': u'http://nohost/plone/oc_checkout',
        }

        self.assertEqual(expected_token, token)

    @browsing
    def test_oc_checkout_redirects_to_document_in_case_of_failure(self, browser):
        self.login(self.dossier_responsible, browser)
        self.checkout_document(self.document)

        self.login(self.regular_user, browser)
        browser.allow_redirects = False
        browser.open(self.document, view='@@oc_checkout')

        location = browser.headers['location']
        self.assertEqual(302, browser.status_code)
        self.assertEqual(self.document.absolute_url(), location)
