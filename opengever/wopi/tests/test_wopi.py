from base64 import urlsafe_b64encode
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.wopi.token import create_access_token
from plone.uuid.interfaces import IUUID


class TestWOPIView(IntegrationTestCase):

    @browsing
    def test_check_file_info_contains_sha256_checksum(self, browser):
        with self.login(self.regular_user, browser=browser):
            uuid = IUUID(self.document)

        access_token = urlsafe_b64encode(
            create_access_token(self.regular_user.getId(), uuid))

        browser.open('{}/wopi/files/{}?access_token={}'.format(
            self.portal.absolute_url(), uuid, access_token))

        self.assertIn(u'SHA256', browser.json)
        self.assertEqual(
            self.check_file_info()[u'SHA256'],
            u'UdYxdJTszEpzFUYlpoIMtrUNwUVetM8mOZKZ1PnOd7I=',
        )
