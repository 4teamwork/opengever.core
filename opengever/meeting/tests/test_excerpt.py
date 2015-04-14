from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.testing import FunctionalTestCase


class TestExcerpt(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestExcerpt, self).setUp()

        self.repository_root = create(Builder('repository_root'))
        self.repository_folder = create(
            Builder('repository').within(self.repository_root))
        self.dossier = create(
            Builder('dossier').within(self.repository_folder))

        self.templates = create(Builder('templatedossier'))
        self.sablon_template = create(
            Builder('sablontemplate')
            .within(self.templates)
            .with_asset_file('sablon_template.docx'))
        container = create(Builder('committee_container').having(
            pre_protocol_template=self.sablon_template,
            protocol_template=self.sablon_template,
            excerpt_template=self.sablon_template))

        self.committee = create(Builder('committee').within(container))

    def test_default_excerpt_is_configured_on_commitee_container(self):
        self.assertEqual(self.sablon_template,
                         self.committee.get_excerpt_template())

    @browsing
    def test_excerpt_template_can_be_configured_per_commitee(self, browser):
        custom_template = create(
            Builder('sablontemplate')
            .within(self.templates)
            .with_asset_file('sablon_template.docx'))

        browser.login().open(self.committee, view='edit')
        browser.fill({'Excerpt template': custom_template})
        browser.css('#form-buttons-save').first.click()

        self.assertEqual(custom_template,
                         self.committee.get_excerpt_template())
