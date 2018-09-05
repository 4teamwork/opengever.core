from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.meeting.command import MIME_DOCX
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase


class TestSablonTemplateView(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestSablonTemplateView, self).setUp()
        self.templates = create(Builder('templatefolder'))
        self.sablon_template = create(
            Builder('sablontemplate')
            .within(self.templates)
            .with_asset_file('sablon_template.docx'))

    @browsing
    def test_sablon_template_debug_view_returns_rendered_template(self, browser):
        self.grant('Manager')
        browser.login().open(self.sablon_template, view='fill_meeting_template')

        self.assertEqual(browser.headers['content-type'], MIME_DOCX)
        self.assertIsNotNone(browser.contents)

    @browsing
    def test_regular_user_can_add_new_keywords_in_sablon(self, browser):
        self.grant('Reader', 'Contributor', 'Editor')

        browser.login().visit(self.sablon_template, view='@@edit')

        keywords = browser.find_field_by_text(u'Keywords')
        new = browser.css('#' + keywords.attrib['id'] + '_new').first
        new.text = u'NewItem1\nNew Item 2\nN\xf6i 3'
        browser.find_button_by_label('Save').click()

        browser.visit(self.sablon_template, view='edit')
        keywords = browser.find_field_by_text(u'Keywords')
        self.assertTupleEqual(('New Item 2', 'NewItem1', 'N=C3=B6i 3'),
                              tuple(keywords.value))


class TestSablonTemplateMenus(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_action_menu_contents_for_administrator(self, browser):
        expected_menu = ['Checkout', 'Copy Item', 'Properties']
        self.login(self.administrator, browser)
        browser.open(self.sablon_template)
        self.assertItemsEqual(expected_menu, editbar.menu_options("Actions"))

    @browsing
    def test_action_menu_contents_for_manager(self, browser):
        expected_menu = ['Checkout', 'Copy Item', 'Fill meeting template', 'Properties', 'Policy...']
        self.login(self.manager, browser)
        browser.open(self.sablon_template)
        self.assertItemsEqual(expected_menu, editbar.menu_options("Actions"))
