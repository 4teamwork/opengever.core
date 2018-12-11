from ftw.testbrowser import browsing
from opengever.disposition.disposition import IDisposition
from opengever.testing import IntegrationTestCase
from plone.protect import createToken


class TestUpdateTransferNumber(IntegrationTestCase):
    """Test disposition overviews function as intended."""

    @browsing
    def test_update_transfer_number_integration(self, browser):
        self.login(self.archivist, browser)
        browser.open(self.disposition,
                     {'transfer_number': u'Ablieferung 2018-1',
                      '_authenticator': createToken()},
                     view=u'update-transfer-number')

        self.assertEquals({u'proceed': True}, browser.json)
        self.assertEquals(u'Ablieferung 2018-1',
                          IDisposition(self.disposition).transfer_number)
