from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestSablonTemplateDownloadView(FunctionalTestCase):

    def setUp(self):
        super(TestSablonTemplateDownloadView, self).setUp()
        self.grant('Manager')
        self.dossier = create(Builder('templatedossier'))
        self.template = create(
            Builder('sablontemplate')
            .attach_file_containing("blub blub", name=u't\xf6st.txt')
            .within(self.dossier))

    @browsing
    def test_download_sablon_template(self, browser):
        browser.login().open(self.template, view='tabbedview_view-overview')
        browser.find('Download copy').click()
        browser.find('label_download').click()

        self.assertEqual('attachment; filename="tost.txt"',
                         browser.headers['content-disposition'])
        self.assertEqual("blub blub", browser.contents)
