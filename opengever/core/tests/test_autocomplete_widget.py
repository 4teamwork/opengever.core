from ftw.testbrowser import browsing
from ftw.testbrowser.testing import BROWSER_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from unittest2 import TestCase
import os
import plone.protect.auto


class TestOpengeverAutocompleteWidgetForTestbrowser(TestCase):
    """
    We have a custom autocomplete widget which uses "term" instead
    of "q" as query parameter and returns different results.
    """

    layer = BROWSER_FUNCTIONAL_TESTING

    def setUp(self):
        plone.protect.auto.CSRF_DISABLED = True

    def tearDown(self):
        plone.protect.auto.CSRF_DISABLED = False

    @browsing
    def test_autocomplete_form_fill(self, browser):
        browser.login(SITE_OWNER_NAME).visit(view='test-z3cform-shopping')
        browser.fill({'Payment': 'mastercard'})
        browser.find('Submit').click()
        self.assertEquals({u'payment': [u'mastercard']}, browser.json)

    @browsing
    def test_autocomplete_query(self, browser):
        browser.login(SITE_OWNER_NAME).visit(view='test-z3cform-shopping')

        self.assertEquals([['cash', 'Cash'],
                           ['mastercard', 'MasterCard']],
                          browser.find('Payment').query('ca'))
