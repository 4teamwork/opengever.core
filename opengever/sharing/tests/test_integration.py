from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from opengever.sharing.testing import OPENGEVER_SHARING_INTEGRATION_TESTING
from plone.dexterity.utils import createContentInContainer
from plone.testing.z2 import Browser
import unittest2 as unittest
import transaction


class TestOpengeverJournalIntegration(unittest.TestCase):

    layer = OPENGEVER_SHARING_INTEGRATION_TESTING

    def test_integration_dossier_events(self):
        """ Test Integration of opengever.sharing
        """
        portal = self.layer['portal']

        dossier = createContentInContainer(
            portal, 'opengever.dossier.businesscasedossier', 'd1')

        transaction.commit()
        browser = self.get_browser()

        # We just test to open the views because the rest is tested
        # in other packages
        browser.open('%s/@@sharing' % dossier.absolute_url())
        browser.open('%s/@@tabbedview_view-sharing' % dossier.absolute_url())

    def get_browser(self):
        """Return logged in browser
        """
        # Create browser an login
        portal_url = self.layer['portal'].absolute_url()
        browser = Browser(self.layer['app'])
        browser.open('%s/login_form' % portal_url)
        browser.getControl(name='__ac_name').value = TEST_USER_NAME
        browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
        browser.getControl(name='submit').click()

        # Check login
        self.assertNotEquals('__ac_name' in browser.contents, True)
        self.assertNotEquals('__ac_password' in browser.contents, True)

        return browser
