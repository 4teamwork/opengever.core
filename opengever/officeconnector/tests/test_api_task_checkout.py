from copy import deepcopy
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testing import freeze
from hashlib import sha256
from opengever.officeconnector.testing import FREEZE_DATE
from opengever.officeconnector.testing import JWT_SIGNING_SECRET_PLONE
from opengever.officeconnector.testing import OCIntegrationTestCase
from opengever.testing.assets import path_to_asset
import jwt


class TestOfficeconnectorTaskAPIWithCheckoutWithRESTAPI(OCIntegrationTestCase):

    features = (
        '!officeconnector-attach',
        'officeconnector-checkout',
    )

    @browsing
    def test_foreign_contributor_can_checkout_related_document_on_assigned_task(self, browser):
        self.login(self.regular_user, browser)
        # We get a reference to self.document so the foreign user can access it
        document = self.document

        browser.open(self.dossier)
        factoriesmenu.add('Task')
        browser.fill({
            'Title': 'Task title',
            'Task Type': 'For direct execution',
            'Related Items': document,
        })
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill(
            ':'.join(('rk', self.foreign_contributor.getId())))
        browser.find('Save').click()

        self.login(self.foreign_contributor, browser)

        with freeze(FREEZE_DATE):
            oc_url = self.fetch_document_checkout_oc_url(browser, document)

        self.assertIsNotNone(oc_url)
        self.assertEqual(200, browser.status_code)

        expected_token = {
            u'action': u'checkout',
            u'documents': [u'createtreatydossiers000000000002'],
            u'exp': 4121033100,
            u'sub': u'james.bond',
            u'url': u'http://nohost/plone/oc_checkout',
            }
        raw_token = oc_url.split(':')[-1]
        token = jwt.decode(raw_token, JWT_SIGNING_SECRET_PLONE, algorithms=('HS256',))
        self.assertEqual(expected_token, token)

        expected_payloads = [{
            u'status': u'status',
            u'checkin': u'@checkin',
            u'checkout': u'@checkout',
            u'content-type': u'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            u'document-url': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14',
            u'download': u'download',
            u'filename': u'Vertraegsentwurf.docx',
            u'lock': u'@lock',
            u'unlock': u'@unlock',
            u'upload': u'@tus-replace',
            u'uuid': u'createtreatydossiers000000000002',
        }]
        payloads = self.fetch_document_checkout_payloads(browser, raw_token, token)
        self.assertEqual(200, browser.status_code)
        for payload, expected_payload in zip(payloads, expected_payloads):
            payload_copy = deepcopy(payload)
            self.assertFalse(payload_copy.pop('csrf-token', None))
            self.assertTrue(payload_copy.pop('reauth', None))
            self.assertEqual(expected_payload, payload_copy)

        self.checkout_document(browser, raw_token, payloads[0], document)
        self.lock_document(browser, raw_token, payloads[0], document)

        original_checksum = sha256(self.download_document(browser, raw_token, payloads[0])).hexdigest()

        with open(path_to_asset('addendum.docx')) as f:
            self.upload_document(browser, raw_token, payloads[0], document, f)

        new_checksum = sha256(self.download_document(browser, raw_token, payloads[0])).hexdigest()
        self.assertNotEqual(new_checksum, original_checksum)

        self.unlock_document(browser, raw_token, payloads[0], document)
        self.checkin_document(browser, raw_token, payloads[0], document)
