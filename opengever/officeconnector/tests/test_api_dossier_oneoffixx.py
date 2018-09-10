from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.officeconnector.testing import FREEZE_DATE
from opengever.officeconnector.testing import JWT_SIGNING_SECRET_PLONE
from opengever.officeconnector.testing import OCIntegrationTestCase
from pkg_resources import resource_string
import jwt


class TestOfficeconnectorDossierAPIWithOneOffixx(OCIntegrationTestCase):
    features = (
        'officeconnector-checkout',
        'oneoffixx'
    )

    @browsing
    def test_create_with_oneoffixx(self, browser):
        self.login(self.dossier_responsible, browser)

        with freeze(FREEZE_DATE):
            oc_url = self.fetch_document_oneoffixx_oc_url(browser, self.shadow_document)

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        expected_token = {
            u'action': u'oneoffixx',
            u'documents': [u'createshadowdocument000000000001'],
            u'exp': 4121033100,
            u'sub': u'robert.ziegler',
            u'url': u'http://nohost/plone/oc_oneoffixx',
            }
        raw_token = oc_url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE)
        self.assertEqual(expected_token, token)

        expected_payloads = [{
            u'connect-xml': u'@@oneoffix_connect_xml',
            u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-37',
            u'filename': None,
            u'uuid': u'createshadowdocument000000000001',
            }]

        payloads = self.fetch_document_oneoffixx_payloads(browser, raw_token, token)
        self.assertEquals(200, browser.status_code)

        for payload, expected_payload in zip(payloads, expected_payloads):
            self.assertTrue(payload.get('csrf-token'))
            self.assertDictContainsSubset(expected_payload, payload)

        expected_oneoffixx_xml = resource_string("opengever.oneoffixx.tests.assets", "oneoffixx_connect_xml.txt")

        with freeze(FREEZE_DATE):
            oneoffixx_xml = self.download_oneoffixx_xml(browser, raw_token, payloads[0])

        self.maxDiff = None
        self.assertEqual(expected_oneoffixx_xml.splitlines(), oneoffixx_xml.splitlines())

        # XXX - this test will continue once we have a fileless shadow document
        # in the fixtures

    @browsing
    def test_create_with_oneoffixx_when_not_shadow_document(self, browser):
        self.login(self.dossier_responsible, browser)
        with browser.expect_http_error(404):
            oc_url = self.fetch_document_oneoffixx_oc_url(browser, self.empty_document)
            self.assertIsNone(oc_url)
