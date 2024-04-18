from base64 import b64encode
from base64 import urlsafe_b64encode
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.wopi.interfaces import IWOPISettings
from opengever.wopi.proof_key import create_message
from opengever.wopi.testing import mock_wopi_discovery
from opengever.wopi.token import create_access_token
from plone import api
from plone.uuid.interfaces import IUUID
from unittest import skip


class TestWOPIView(IntegrationTestCase):

    private_key = None

    def setUp(self):
        super(TestWOPIView, self).setUp()
        self.setup_proof_keys()

    def setup_proof_keys(self):
        if self.private_key is not None:
            return
        self.private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend())
        mock_wopi_discovery(public_key=self.private_key.public_key())

    def get_signature(self, access_token, url, timestamp):
        return b64encode(self.private_key.sign(
            create_message(access_token, url, timestamp),
            padding.PKCS1v15(),
            hashes.SHA256(),
        ))

    def wopi_headers(self, access_token, url):
        timestamp = str(int(
            (datetime.utcnow() - datetime(1, 1, 1)).total_seconds() * 10000000))
        return {
            'X-WOPI-TimeStamp': timestamp,
            'X-WOPI-Proof': self.get_signature(access_token, url, timestamp),
            'X-WOPI-ProofOld': self.get_signature(access_token, url, timestamp),
        }

    @browsing
    def check_file_info(self, browser):
        with self.login(self.regular_user, browser=browser):
            uuid = IUUID(self.document)

        access_token = urlsafe_b64encode(
            create_access_token(self.regular_user.getId(), uuid))
        url = '{}/wopi/files/{}?access_token={}'.format(
            self.portal.absolute_url(), uuid, access_token)

        browser.open(url, headers=self.wopi_headers(access_token, url))
        return browser.json

    def test_check_file_info_contains_sha256_checksum(self):
        self.assertIn(u'SHA256', self.check_file_info())
        self.assertEqual(
            self.check_file_info()[u'SHA256'],
            u'UdYxdJTszEpzFUYlpoIMtrUNwUVetM8mOZKZ1PnOd7I=',
        )

    def test_check_file_info_contains_license_check_flag_if_business_user(self):
        self.assertIn(u'LicenseCheckForEditIsEnabled', self.check_file_info())
        self.assertEqual(
            self.check_file_info()[u'LicenseCheckForEditIsEnabled'],
            True,
        )

    def test_check_file_info_has_no_license_check_flag_if_not_business_user(self):
        api.portal.set_registry_record(name='business_user', interface=IWOPISettings, value=False)
        self.assertNotIn(u'LicenseCheckForEditIsEnabled', self.check_file_info())

    def test_check_file_info_contains_host_edit_url(self):
        self.assertIn(u'HostEditUrl', self.check_file_info())
        self.assertEqual(
            self.check_file_info()[u'HostEditUrl'],
            u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/document-14/office_online_edit',
        )

    def test_breadcrumbBrandName_is_portal_title(self):
        self.assertIn(u'BreadcrumbBrandName', self.check_file_info())
        self.assertEqual('Plone site', self.check_file_info()[u'BreadcrumbBrandName'])

    def test_owner_id_falls_back_to_owner_if_creator_is_missing(self):
        with self.login(self.regular_user):
            self.document.setCreators('')
            assert self.document.Creator() == ''

        self.assertIn('OwnerId', self.check_file_info())
        self.assertEqual('robert.ziegler', self.check_file_info()['OwnerId'])
