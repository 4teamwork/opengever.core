from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestLivesearchReply(IntegrationTestCase):

    @browsing
    def test_livesearch_reply_escapes_title(self, browser):
        self.login(self.regular_user, browser=browser)

        self.dossier.title = u"<script>alert('evil');</script>"
        self.dossier.reindexObject()

        browser.open(view='livesearch_reply?q=evil')
        link_node = browser.css('.LSRow').first
        # lxml unescapes attributes for us. we want to test that the title
        # has been escaped correctly and thus use browser.contents only.
        self.assertIn('title="&lt;script&gt;alert(\'evil\');&lt;/script&gt;"',
                      link_node.outerHTML)
        # also test title that is displayed
        self.assertIn('&lt;script&gt;alert(\'evil\');&lt;',
                      link_node.innerHTML)
