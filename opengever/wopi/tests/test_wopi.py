from base64 import urlsafe_b64encode
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.wopi.interfaces import IWOPISettings
from opengever.wopi.token import create_access_token
from plone import api
from plone.uuid.interfaces import IUUID


class TestWOPIView(IntegrationTestCase):

    @browsing
    def check_file_info(self, browser):
        with self.login(self.regular_user, browser=browser):
            uuid = IUUID(self.document)

        access_token = urlsafe_b64encode(
            create_access_token(self.regular_user.getId(), uuid))

        browser.open('{}/wopi/files/{}?access_token={}'.format(
            self.portal.absolute_url(), uuid, access_token))
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
