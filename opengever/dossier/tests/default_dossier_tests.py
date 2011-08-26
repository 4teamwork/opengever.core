from plone.testing.z2 import Browser
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
import transaction
import unittest2 as unittest
from opengever.dossier.testing import OPENGEVER_DOSSIER_INTEGRATION_TESTING


class TestDefaultDossierFunctions(unittest.TestCase):
    """Base Tests to test the default functions for all dossier-types

    let your testobject inherit from this class to extend it with default
    dossier-tests.
    The none-parameter-tests will start automatically, and the parameter-
    tests you have to call explicitly in a test_method:
    """

    # Set this to the dossier you like to test
    dossier_name = ''
    layer = OPENGEVER_DOSSIER_INTEGRATION_TESTING
    tabs = ['Common', 'Filing', 'Life Cycle', 'Classification']

    # Default none parameter-tests (start automatically)
    # ***************************************************

    def get_browser(self):
        """Return logged in browser
        """
        portal_url = self.layer['portal'].absolute_url()
        browser = Browser(self.layer['app'])
        browser.open('%s/login_form' % portal_url)
        browser.getControl(name='__ac_name').value = TEST_USER_NAME
        browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
        browser.getControl(name='submit').click()

        return browser

    def get_add_view(self):
        """Return the a browser whos content is in the add-view of a dossier
        """

        url = self.layer['portal'].absolute_url()

        browser = self.get_browser()
        browser.open('%s/++add++%s' % (url, self.dossier_name))
        return browser

    def create_dossier(self, parent_location=None, name="dossier1"):
        """Create and return a dossier in a given location
        """
        location = self.layer['portal']
        if parent_location:
            location = parent_location

        dossier = location[location.invokeFactory(self.dossier_name, name)]
        transaction.commit()
        return dossier


    # Tests

    def test_default_values(self):
        """Check the default values of the document
        """
        browser = self.get_add_view()
        responsible = browser.getControl(name='form.widgets.IDossier.responsible:list').value
        self.assertNotEquals(None, responsible)

    def test_default_tabs(self):

        browser = self.get_add_view()

        for tab in self.tabs:

            # For exact search
            tab = "%s</legend>" % tab
            self.assertEquals(tab in browser.contents, True)


    def default_formular_lables(self, obj):
        pass

    def nesting_deepth(self, obj):
        pass


