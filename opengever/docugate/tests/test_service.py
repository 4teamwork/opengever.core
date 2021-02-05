from opengever.testing import IntegrationTestCase
from ftw.testbrowser import browsing
from plone.uuid.interfaces import IUUID
import json


class TestOfficeConnectorDocugatePayload(IntegrationTestCase):

    features = ("officeconnector-checkout", "docugate")

    @browsing
    def test_oc_docugate_returns_document_url(self, browser):
        self.login(self.dossier_responsible, browser)

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        resp = browser.open(
            self.portal,
            method='POST',
            data=json.dumps([IUUID(self.shadow_document)]),
            headers=headers,
            view='oc_docugate',
        ).json

        self.assertIn(u'csrf-token', resp[0])
        # Provide a static csrf token
        resp[0][u'csrf-token'] = u'3d1befb138adae65000f0d5c6b67ad77fce29e2f'

        self.assertEqual(
            resp,
            [{
                u'csrf-token': u'3d1befb138adae65000f0d5c6b67ad77fce29e2f',
                u'docugate-xml': u'@@docugate-xml',
                u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/'
                u'vertrage-und-vereinbarungen/dossier-1/document-41',
                u'uuid': u'createshadowdocument000000000001',
            }]
        )

    @browsing
    def test_oc_docugate_returns_404_if_not_shadow_document(self, browser):
        self.login(self.dossier_responsible, browser)

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        with browser.expect_http_error(404):
            browser.open(
                self.portal,
                method='POST',
                data=json.dumps([IUUID(self.document)]),
                headers=headers,
                view='oc_docugate',
            )
