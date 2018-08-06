from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testing import freeze
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
        self.document.file = None
        self.document.as_shadow_document()

        with freeze(datetime(2100, 8, 3, 15, 25)):
            oc_url = self.fetch_document_oneoffixx_oc_url(browser, self.document)

        self.assertIsNotNone(oc_url)
        self.assertEquals(200, browser.status_code)

        expected_token = {
            u'action': u'oneoffixx',
            u'documents': [u'createtreatydossiers000000000002'],
            u'exp': 4121033100,
            u'sub': u'robert.ziegler',
            u'url': u'http://nohost/plone/oc_oneoffixx',
            }
        raw_token = oc_url.split(':')[-1]
        token = jwt.decode(raw_token, verify=False)
        self.assertEqual(token, expected_token)

        expected_payloads = [{
            u'checkout-url': u'oc:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
                             u'.eyJhY3Rpb24iOiJjaGVja291dCIsInVybCI6Imh0dHA6Ly9ub2hvc3QvcGxvbmUvb2NfY2hlY2tvdXQiLCJkb2N1bWV'
                             u'udHMiOlsiY3JlYXRldHJlYXR5ZG9zc2llcnMwMDAwMDAwMDAwMDIiXSwic3ViIjoicm9iZXJ0LnppZWdsZXIiLCJleHA'
                             u'iOjQxMjEwMzMxMDB9'
                             u'.9WnbmlXRe9rEOnBdJBVO0y7Di7Zga3mgncFv0grS2H8',
            u'connect-xml': u'@@oneoffix_connect_xml',
            u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-12',
            u'filename': None,
            u'uuid': u'createtreatydossiers000000000002',
            }]
        with freeze(datetime(2100, 8, 3, 15, 25)):
            payloads = self.fetch_document_oneoffixx_payloads(browser, raw_token, token)
        self.assertEquals(200, browser.status_code)
        for payload, expected_payload in zip(payloads, expected_payloads):
            self.assertTrue(payload.get('csrf-token'))
            self.assertDictContainsSubset(expected_payload, payload)

        expected_token = {
            u'action': u'checkout',
            u'documents': [u'createtreatydossiers000000000002'],
            u'exp': 4121033100,
            u'sub': u'robert.ziegler',
            u'url': u'http://nohost/plone/oc_checkout',
            }
        raw_token = payloads[0].get('checkout-url').split(':')[-1]
        token = jwt.decode(raw_token, verify=False)
        self.assertEqual(token, expected_token)

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
            '      <Arguments/>',
            '      <Function name="CustomInterfaceConnector" id="70E94788-CE84-4460-9698-5663878A295B">',
            '        <Arguments>',
            '          <Interface Name="OneGovGEVER">',
            '            <Node Id="ogg.document.title">Vertr&#228;gsentwurf</Node>',
            '            <Node Id="ogg.document.reference_number">Client1 1.1 / 1 / 12</Node>',
            '            <Node Id="ogg.document.sequence_number">12</Node>',
            '          </Interface>',
            '        </Arguments>',
            '      </Function>',
            '      <Function name="MetaData" id="c364b495-7176-4ce2-9f7c-e71f302b8096">',
            '        <Value key="ogg.document.title" type="string">Vertr&#228;gsentwurf</Value>',
            '        <Value key="ogg.document.reference_number" type="string">Client1 1.1 / 1 / 12</Value>',
            '        <Value key="ogg.document.sequence_number" type="string">12</Value>',
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
        self.assertEqual(oneoffixx_xml, expected_oneoffixx_xml)

        # XXX - this test will continue once we have a fileless shadow document
        # in the fixtures

    @browsing
    def test_create_with_oneoffixx_when_not_shadow_document(self, browser):
        self.login(self.dossier_responsible, browser)
        self.document.file = None

        with browser.expect_http_error(404):
            oc_url = self.fetch_document_oneoffixx_oc_url(browser, self.document)

            self.assertIsNone(oc_url)
