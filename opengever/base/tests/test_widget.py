from ftw.testbrowser import browsing
from opengever.base.widgets import trix_strip_whitespace
from opengever.testing import FunctionalTestCase
from plone.app.z3cform.interfaces import IPloneFormLayer
from unittest import TestCase
from z3c.form.browser.text import TextWidget
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.schema._bootstrapfields import TextLine


class TestGeverRenderWidget(FunctionalTestCase):
    def setUp(self):
        super(TestGeverRenderWidget, self).setUp()
        textfield = TextLine()
        textfield.description = u"A d\xfcscription"

        self.widget = TextWidget(self.request)
        self.widget.field = textfield

        alsoProvides(self.request, IPloneFormLayer)

    @browsing
    def test_display_default_field_description(self, browser):
        view = getMultiAdapter((self.widget, self.request),
                               name="ploneform-render-widget")

        browser.open_html(view())

        self.assertEqual(
            u'A d\xfcscription',
            browser.css('.formHelp').first.text)

    @browsing
    def test_dispaly_dynamic_description_if_available(self, browser):
        self.widget.dynamic_description = u"A d\xfcnamic description"

        view = getMultiAdapter((self.widget, self.request),
                               name="ploneform-render-widget")

        browser.open_html(view())

        self.assertEqual(
            u'A d\xfcnamic description',
            browser.css('.formHelp').first.text)

    @browsing
    def test_escape_dynamic_description(self, browser):
        self.widget.dynamic_description = u"<script>alert('bad');</script>"

        widget_renderer = getMultiAdapter(
            (self.widget, self.request), name='ploneform-render-widget')

        self.assertEqual(
            u'&lt;script&gt;alert(&apos;bad&apos;);&lt;/script&gt;',
            widget_renderer.get_description())


class TestTrixWidget(FunctionalTestCase):

    def setUp(self):
        super(TestTrixWidget, self).setUp()
        self.grant('Manager')

    @browsing
    def test_fill_trix_field_with_browser(self, browser):
        browser.login().visit(view='test-z3cform-widget')

        self.assertEqual(1, len(browser.css('trix-toolbar')))
        self.assertEqual(1, len(browser.css('.trix-editor-proxy')))

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


class TestRadioTableWidget(FunctionalTestCase):

    @browsing
    def test_renders_default_table_columns(self, browser):
        browser.login().visit(view='test-z3cform-widget')

        self.assertEqual(
            # checkbox-column title/text is empty and that's ok.
            [{'': '', 'Title': 'foo'},
             {'': '', 'Title': 'bar'}],
            browser.css('#formfield-form-widgets-default_radio_table_field '
                        'table').first.dicts()
        )

    @browsing
    def test_renders_custom_table_columns(self, browser):
        browser.login().visit(view='test-z3cform-widget')

        self.assertEqual(
            # checkbox-column title/text is empty and that's ok.
            [{'': '', 'Description': 'Odi et amo.'},
             {'': '', 'Description': 'Quare id faciam fortasse requiris?'}],
            browser.css('#formfield-form-widgets-custom_radio_table_field '
                        'table').first.dicts()
        )

    @browsing
    def test_fill_table_choice_field(self, browser):
        browser.login().visit(view='test-z3cform-widget')
        browser.fill({'form.widgets.default_radio_table_field': '2'}).submit()

        self.assertEqual(
            {u'default_radio_table_field': [2, u'bar']}, browser.json)

    @browsing
    def test_renders_table_choice_input_fields(self, browser):
        browser.login().visit(view='test-z3cform-widget')
        inputs = browser.css(
            '#formfield-form-widgets-default_radio_table_field input')
        expected_inputs = [
            u'<input type="text" name="searchable_text" class="inputLabel tableradioSearchbox" autocomplete="false" '
            u'placeholder="Filter" title="Filter">',
            u'<input id="form-widgets-default_radio_table_field-1" '
            u'name="form.widgets.default_radio_table_field" value="1" title="foo" type="radio">',
            u'<input id="form-widgets-default_radio_table_field-2" '
            u'name="form.widgets.default_radio_table_field" value="2" title="bar" type="radio">',
            u'<input name="form.widgets.default_radio_table_field-empty-marker" type="hidden" value="1">',
            ]
        self.assertEqual(expected_inputs, [each.normalized_outerHTML for each in inputs])

    @browsing
    def test_renders_empty_message(self, browser):
        browser.login().visit(view='test-z3cform-widget')
        self.assertEqual(
            "No items available",
            browser.css('#formfield-form-widgets-empty_radio_table_field .empty_message').first.text
        )


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
