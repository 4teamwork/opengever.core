from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from plone.app.z3cform.interfaces import IPloneFormLayer
from z3c.form.browser.text import TextWidget
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.schema._bootstrapfields import TextLine


class TestGeverRenderWidget(IntegrationTestCase):
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


class TestRadioTableWidget(IntegrationTestCase):

    @browsing
    def test_renders_default_table_columns(self, browser):
        self.login(self.manager, browser=browser)
        browser.open(view='test-z3cform-widget')

        self.assertEqual(
            # checkbox-column title/text is empty and that's ok.
            [{'': '', 'Title': 'None'}, {'': '', 'Title': 'foo'}, {'': '', 'Title': 'bar'}],
            browser.css('#formfield-form-widgets-default_radio_table_field table').first.dicts(),
            )

    @browsing
    def test_renders_custom_table_columns(self, browser):
        self.login(self.manager, browser=browser)
        browser.open(view='test-z3cform-widget')

        # checkbox-column title/text is empty and that's ok.
        expected_columns = [
            {'': '', 'Description': ''},
            {'': '', 'Description': 'Odi et amo.'},
            {'': '', 'Description': 'Quare id faciam fortasse requiris?'},
            ]
        self.assertEqual(
            expected_columns,
            browser.css('#formfield-form-widgets-custom_radio_table_field table').first.dicts(),
            )

    @browsing
    def test_does_not_render_none_choice_when_a_required_field(self, browser):
        self.login(self.manager, browser=browser)
        browser.open(view='test-z3cform-required-widget')
        self.assertNotIn(
            {'': '', 'Description': ''},
            browser.css('#formfield-form-widgets-required_radio_table_field table').first.dicts(),
            )

    @browsing
    def test_fill_table_choice_field(self, browser):
        self.login(self.manager, browser=browser)
        browser.open(view='test-z3cform-widget')

        browser.fill({'form.widgets.default_radio_table_field': '2'}).submit()
        self.assertEqual({u'default_radio_table_field': [2, u'bar']}, browser.json)

    @browsing
    def test_renders_table_choice_input_fields(self, browser):
        self.login(self.manager, browser=browser)
        browser.open(view='test-z3cform-widget')

        inputs = browser.css(
            '#formfield-form-widgets-default_radio_table_field input')
        expected_inputs = [
            u'<input type="text" name="searchable_text" class="inputLabel tableradioSearchbox" autocomplete="false" placeholder="Filter" title="Filter">',  # noqa
            u'<input id="form-widgets-default_radio_table_field-empty-marker" name="form.widgets.default_radio_table_field" value="--NOVALUE--" title="label_none" type="radio">',  # noqa
            u'<input id="form-widgets-default_radio_table_field-1" name="form.widgets.default_radio_table_field" value="1" title="foo" type="radio">',  # noqa
            u'<input id="form-widgets-default_radio_table_field-2" name="form.widgets.default_radio_table_field" value="2" title="bar" type="radio">',  # noqa
            u'<input name="form.widgets.default_radio_table_field-empty-marker" type="hidden" value="1">',
            ]
        self.assertEqual(expected_inputs, [each.normalized_outerHTML for each in inputs])

    @browsing
    def test_renders_empty_message(self, browser):
        self.login(self.manager, browser=browser)
        browser.open(view='test-z3cform-widget')

        self.assertEqual(
            "No items available",
            browser.css('#formfield-form-widgets-empty_radio_table_field .empty_message').first.text
        )
