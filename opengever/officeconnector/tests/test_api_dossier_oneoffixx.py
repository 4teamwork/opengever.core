from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.officeconnector.testing import FREEZE_DATE
from opengever.officeconnector.testing import JWT_SIGNING_SECRET_PLONE
from opengever.officeconnector.testing import OCIntegrationTestCase
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
            u'checkout-url': u'oc:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
                             u'.eyJhY3Rpb24iOiJjaGVja291dCIsInVybCI6Imh0dHA6Ly9ub2hvc3QvcGxvbmUvb2NfY2hlY2tvdXQiLCJkb2N1bWV'
                             u'udHMiOlsiY3JlYXRlc2hhZG93ZG9jdW1lbnQwMDAwMDAwMDAwMDEiXSwic3ViIjoicm9iZXJ0LnppZWdsZXIiLCJleHA'
                             u'iOjQxMjEwMzMxMDB9'
                             u'.tf1OL0GixVdQv9OBiItrblq3B9Q46jQOwT8kK8CXyDo',
            u'connect-xml': u'@@oneoffix_connect_xml',
            u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-37',
            u'filename': None,
            u'uuid': u'createshadowdocument000000000001',
            }]
        with freeze(FREEZE_DATE):
            payloads = self.fetch_document_oneoffixx_payloads(browser, raw_token, token)
        self.assertEquals(200, browser.status_code)
        for payload, expected_payload in zip(payloads, expected_payloads):
            self.assertTrue(payload.get('csrf-token'))
            self.assertDictContainsSubset(expected_payload, payload)

        expected_token = {
            u'action': u'checkout',
            u'documents': [u'createshadowdocument000000000001'],
            u'exp': 4121033100,
            u'sub': u'robert.ziegler',
            u'url': u'http://nohost/plone/oc_checkout',
            }
        raw_token = payloads[0].get('checkout-url').split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE)
        self.assertEqual(expected_token, token)

        expected_oneoffixx_xml = [
            '<OneOffixxConnectBatch xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xmlns="http://schema.oneoffixx.com/OneOffixxConnectBatch/1">',
            '  <Settings>',
            '    <Add key="KeepConnector">true</Add>',
            '    <Add key="CreateConnectorResultOnError">true</Add>',
            '    <Add key="CreateConnectorResult">true</Add>',
            '  </Settings>',
            '  <Entries>',
            '    <OneOffixxConnect>',
            '      <Arguments>',
            '        <TemplateId>2574d08d-95ea-4639-beab-3103fe4c3bc7</TemplateId>',
            '        <LanguageLcid>2055</LanguageLcid>',
            '      </Arguments>',
            '      <Function name="CustomInterfaceConnector" id="70E94788-CE84-4460-9698-5663878A295B">',
            '        <Arguments>',
            '          <Interface Name="OneGovGEVER">',
            '            <Node Id="ogg.document.title">Sch&#228;ttengarten</Node>',
            '            <Node Id="ogg.document.reference_number">Client1 1.1 / 1 / 37</Node>',
            '            <Node Id="ogg.document.sequence_number">37</Node>',
            '          </Interface>',
            '        </Arguments>',
            '      </Function>',
            '      <Function name="MetaData" id="c364b495-7176-4ce2-9f7c-e71f302b8096">',
            '        <Value key="ogg.document.title" type="string">Sch&#228;ttengarten</Value>',
            '        <Value key="ogg.document.reference_number" type="string">Client1 1.1 / 1 / 37</Value>',
            '        <Value key="ogg.document.sequence_number" type="string">37</Value>',
            '      </Function>',
            '      <Commands>',
            '        <Command Name="DefaultProcess">',
            '          <Parameters>',
            '            <Add key="start">false</Add>',
            '          </Parameters>',
            '        </Command>',
            '        <Command Name="SaveAs">',
            '          <Parameters>',
            '            <Add key="Overwrite">true</Add>',
            '            <Add key="CreateFolder">true</Add>',
            '            <Add key="AllowUpdateDocumentPart">false</Add>',
            '            <Add key="Filename"></Add>',
            '          </Parameters>',
            '        </Command>',
            '        <Command Name="ConvertToDocument"/>',
            '      </Commands>',
            '    </OneOffixxConnect>',
            '  </Entries>',
            '</OneOffixxConnectBatch>',
            ]
        oneoffixx_xml = self.download_oneoffixx_xml(browser, raw_token, payloads[0]).splitlines()
        self.assertEqual(expected_oneoffixx_xml, oneoffixx_xml)

        # XXX - this test will continue once we have a fileless shadow document
        # in the fixtures

    @browsing
    def test_create_with_oneoffixx_when_not_shadow_document(self, browser):
        self.login(self.dossier_responsible, browser)
        with browser.expect_http_error(404):
            oc_url = self.fetch_document_oneoffixx_oc_url(browser, self.empty_document)
            self.assertIsNone(oc_url)
