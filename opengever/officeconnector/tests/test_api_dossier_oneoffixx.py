from copy import deepcopy
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.officeconnector.testing import FREEZE_DATE
from opengever.officeconnector.testing import JWT_SIGNING_SECRET_PLONE
from opengever.officeconnector.testing import OCIntegrationTestCase
from opengever.testing.assets import path_to_asset
from pkg_resources import resource_string
import jwt
import re
import xml.etree.ElementTree as ET


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
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertEqual(expected_token, token)

        expected_payloads = [{
            u'connect-xml': u'@@oneoffix_connect_xml',
            u'content-type': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-33',
            u'filename': None,
            u'uuid': u'createshadowdocument000000000001',
            }]

        payloads = self.fetch_document_oneoffixx_payloads(browser, raw_token, token)
        self.assertEquals(200, browser.status_code)

        for payload, expected_payload in zip(payloads, expected_payloads):
            self.assertTrue(payload.pop('csrf-token', None))
            self.assertEqual(expected_payload, payload)

        expected_oneoffixx_xml = resource_string("opengever.oneoffixx.tests.assets", "oneoffixx_connect_xml.txt")

        with freeze(FREEZE_DATE):
            oneoffixx_xml = self.download_oneoffixx_xml(browser, raw_token, payloads[0])

        self.maxDiff = None
        self.assertEqual(expected_oneoffixx_xml.splitlines(), oneoffixx_xml.splitlines())

        tree = ET.ElementTree(ET.fromstring(oneoffixx_xml))
        namespace = re.match(r'\{.*\}', tree.getroot().tag).group(0)
        namespace_url = namespace.strip('{}')
        ET.register_namespace('', namespace_url)
        ET.register_namespace('xsi', 'http://www.w3.org/2001/XMLSchema-instance')

        raw_token = tree.find(
            './/{namespace}Command[@Name="InvokeProcess"]'
            '/{namespace}Parameters'
            '/{namespace}Add[@key="Arguments"]'
            .format(namespace=namespace)
        ).text.split(':')[-1]
        expected_token = {
            u'action': u'checkout',
            u'documents': [u'createshadowdocument000000000001'],
            u'exp': 4121033100,
            u'sub': u'robert.ziegler',
            u'url': u'http://nohost/plone/oc_checkout',
        }
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertEqual(expected_token, token)

        expected_payloads = [{
            u'checkin-with-comment': u'@@checkin_document',
            u'checkin-without-comment': u'checkin_without_comment',
            u'checkout': u'@@checkout_documents',
            u'content-type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-33',
            u'download': u'download',
            u'filename': None,
            u'upload-form': u'file_upload',
            u'uuid': u'createshadowdocument000000000001',
        }]
        # XXX - As the last document we touched was XML and we touched XML
        # namespacing after that, we'll need to reset the browser to circumvent
        # an ftw.testbrowser bug
        browser.reset()
        payloads = self.fetch_document_checkout_payloads(browser, raw_token, token)
        self.assertEquals(200, browser.status_code)
        for payload, expected_payload in zip(payloads, expected_payloads):
            payload_copy = deepcopy(payload)
            self.assertTrue(payload_copy.pop('csrf-token', None))
            self.assertFalse(payload_copy.pop('reauth', None))
            self.assertEqual(expected_payload, payload_copy)

        self.assertTrue(self.shadow_document.is_shadow_document())
        self.checkout_document(browser, raw_token, payloads[0], self.shadow_document)
        lock_token = self.lock_document(browser, raw_token, self.shadow_document)

        with open(path_to_asset('addendum.docx')) as f:
            self.upload_document(browser, raw_token, payloads[0], self.shadow_document, f)
        self.assertFalse(self.shadow_document.is_shadow_document())

        self.unlock_document(browser, raw_token, self.shadow_document, lock_token)
        self.checkin_document(browser, raw_token, payloads[0], self.shadow_document, comment='foobar')

    @browsing
    def test_create_with_oneoffixx_when_not_shadow_document(self, browser):
        self.login(self.dossier_responsible, browser)
        with browser.expect_http_error(404):
            oc_url = self.fetch_document_oneoffixx_oc_url(browser, self.empty_document)
            self.assertIsNone(oc_url)


class TestOfficeconnectorDossierAPIWithOneOffixxWithRESTAPI(TestOfficeconnectorDossierAPIWithOneOffixx):
    features = (
        'officeconnector-checkout',
        'officeconnector-restapi',
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
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertEqual(expected_token, token)

        expected_payloads = [{
            u'connect-xml': u'@@oneoffix_connect_xml',
            u'content-type': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-33',
            u'filename': None,
            u'uuid': u'createshadowdocument000000000001',
            }]

        payloads = self.fetch_document_oneoffixx_payloads(browser, raw_token, token)
        self.assertEquals(200, browser.status_code)

        for payload, expected_payload in zip(payloads, expected_payloads):
            self.assertTrue(payload.pop('csrf-token', None))
            self.assertEqual(expected_payload, payload)

        expected_oneoffixx_xml = resource_string("opengever.oneoffixx.tests.assets", "oneoffixx_connect_xml.txt")

        with freeze(FREEZE_DATE):
            oneoffixx_xml = self.download_oneoffixx_xml(browser, raw_token, payloads[0])

        self.maxDiff = None
        self.assertEqual(expected_oneoffixx_xml.splitlines(), oneoffixx_xml.splitlines())

        tree = ET.ElementTree(ET.fromstring(oneoffixx_xml))
        namespace = re.match(r'\{.*\}', tree.getroot().tag).group(0)
        namespace_url = namespace.strip('{}')
        ET.register_namespace('', namespace_url)
        ET.register_namespace('xsi', 'http://www.w3.org/2001/XMLSchema-instance')

        raw_token = tree.find(
            './/{namespace}Command[@Name="InvokeProcess"]'
            '/{namespace}Parameters'
            '/{namespace}Add[@key="Arguments"]'
            .format(namespace=namespace)
        ).text.split(':')[-1]
        expected_token = {
            u'action': u'checkout',
            u'documents': [u'createshadowdocument000000000001'],
            u'exp': 4121033100,
            u'sub': u'robert.ziegler',
            u'url': u'http://nohost/plone/oc_checkout',
        }
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertEqual(expected_token, token)

        expected_payloads = [{
            u'status': u'status',
            u'checkin': u'@checkin',
            u'checkout': u'@checkout',
            u'content-type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-33',
            u'download': u'download',
            u'filename': None,
            u'lock': u'@lock',
            u'unlock': u'@unlock',
            u'upload': u'@tus-replace',
            u'uuid': u'createshadowdocument000000000001',
        }]
        # XXX - As the last document we touched was XML and we touched XML
        # namespacing after that, we'll need to reset the browser to circumvent
        # an ftw.testbrowser bug
        browser.reset()
        payloads = self.fetch_document_checkout_payloads(browser, raw_token, token)
        self.assertEquals(200, browser.status_code)
        for payload, expected_payload in zip(payloads, expected_payloads):
            payload_copy = deepcopy(payload)
            self.assertFalse(payload_copy.pop('csrf-token', None))
            self.assertTrue(payload_copy.pop('reauth', None))
            self.assertEqual(expected_payload, payload_copy)

        self.assertTrue(self.shadow_document.is_shadow_document())
        self.checkout_document_via_api(browser, raw_token, payloads[0], self.shadow_document)
        self.lock_document_via_api(browser, raw_token, payloads[0], self.shadow_document)

        with open(path_to_asset('addendum.docx')) as f:
            self.upload_document_via_api(browser, raw_token, payloads[0], self.shadow_document, f)
        self.assertFalse(self.shadow_document.is_shadow_document())

        self.unlock_document_via_api(browser, raw_token, payloads[0], self.shadow_document)
        self.checkin_document_via_api(browser, raw_token, payloads[0], self.shadow_document, comment='foobar')
