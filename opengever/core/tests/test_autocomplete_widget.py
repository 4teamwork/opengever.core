from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from unittest2 import TestCase
import plone.protect.auto


class TestOpengeverAutocompleteWidgetForTestbrowser(TestCase):
    """
    We have a custom autocomplete widget which uses "term" instead
    of "q" as query parameter and returns different results.
    """

    layer = OPENGEVER_FUNCTIONAL_TESTING

    def setUp(self):
        plone.protect.auto.CSRF_DISABLED = True

    def tearDown(self):
        plone.protect.auto.CSRF_DISABLED = False

    @browsing
    def test_autocomplete_form_fill(self, browser):
        browser.login(SITE_OWNER_NAME).visit(view='test-user-selection')
        browser.fill({'Select users': 'hans'})
        browser.find('Submit').click()
        self.assertEquals({u'users': [u'hans']}, browser.json)

    @browsing
    def test_autocomplete_query(self, browser):
        browser.login(SITE_OWNER_NAME).visit(view='test-user-selection')

        self.assertEquals([[u'hans', u'Hans M\xfcller'],
                           [u'hugo', u'Hugo Boss']],
                          browser.find('Select users').query('h'))
