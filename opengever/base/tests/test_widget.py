from ftw.testbrowser import browsing
from opengever.base.widgets import trix_strip_whitespace
from opengever.testing import FunctionalTestCase
from unittest2 import TestCase


class TestWidget(FunctionalTestCase):

    def setUp(self):
        super(TestWidget, self).setUp()
        self.grant('Manager')

    @browsing
    def test_fill_trix_field_with_browser(self, browser):
        browser.login().visit(view='test-z3cform-widget')

        self.assertEqual(1, len(browser.css('trix-toolbar')))
        self.assertEqual(1, len(browser.css('trix-editor')))

        browser.fill({u'trix_field': u'<div>P\xe4ter</div>'}).submit()
        self.assertEquals({u'trix_field': u'<div>P\xe4ter</div>'},
                          browser.json)

    @browsing
    def test_trix_field_is_xss_safe(self, browser):
        browser.login().visit(view='test-z3cform-widget')

        browser.fill({
            u'trix_field':
            u'<div onclick="alert(\'foo\');">P\xe4ter<script>alert("foo");</script></div>'
        }).submit()
        self.assertEquals({u'trix_field': u'<div>P\xe4ter</div>'},
                          browser.json)


class TestUnitTrixStripWhitespace(TestCase):

    def test_preserves_none(self):
        self.assertIsNone(trix_strip_whitespace(None))

    def test_preserves_empty_string(self):
        self.assertEqual(u'', trix_strip_whitespace(u''))

    def test_strips_leading_whitepace(self):
        self.assertEqual(
            u'<div>f\xf6  \nbar</div>',
            trix_strip_whitespace(u'<div>\t&nbsp; <br> \n\r\v  f\xf6  \nbar</div>'))

    def test_strips_trailing_whitespace(self):
        self.assertEqual(
            u'<div>b\xe4r\t\r\nqux</div>',
            trix_strip_whitespace(u'<div>b\xe4r\t\r\nqux&nbsp;&nbsp;<br /><br/> \n</div>'))
