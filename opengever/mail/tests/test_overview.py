from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestMailOverview(IntegrationTestCase):

    @browsing
    def test_description_is_intelligently_formatted(self, browser):
        self.login(self.regular_user, browser)
        self.mail_eml.description = u'\n\n Foo\n    Bar\n'
        browser.open(self.mail_eml, view='tabbedview_view-overview')
        # Somehow what is `&nbsp;` in a browser is `\xa0` in ftw.testbrowser
        self.assertEqual(
            u'<br><br>\xa0Foo<br>\xa0\xa0\xa0\xa0Bar<br>',
            browser.css('#form-widgets-IDocumentMetadata-description')[0].innerHTML,
        )
