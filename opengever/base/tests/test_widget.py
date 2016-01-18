from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


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
