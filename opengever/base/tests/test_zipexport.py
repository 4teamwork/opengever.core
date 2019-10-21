from ftw.testbrowser import browsing
from ftw.zipexport.zipfilestream import ZipFile
from opengever.testing import IntegrationTestCase
from StringIO import StringIO


class TestZipExportView(IntegrationTestCase):

    @browsing
    def test_zip_selected_files(self, browser):
        self.login(self.regular_user, browser=browser)

        docs = [self.document, self.subdocument]
        data = {'zip_selected:method': 1}
        data.update(self.make_path_param(*docs))
        # /plone/ordnungssystem/...

        browser.open(self.dossier, data=data)

        zipfile = ZipFile(StringIO(browser.contents), 'r')
        self.assertEquals(
            [doc.file.filename for doc in docs], zipfile.namelist())

    @browsing
    def test_zip_selected_files_with_pseudorelative_paths(self, browser):
        self.login(self.regular_user, browser=browser)

        docs = [self.document, self.subdocument]
        data = {'zip_selected:method': 1}
        data.update(self.make_pseudorelative_path_param(*docs))
        # /ordnungssystem/...

        browser.open(self.dossier, data=data)

        zipfile = ZipFile(StringIO(browser.contents), 'r')
        self.assertEquals(
            [doc.file.filename for doc in docs], zipfile.namelist())
