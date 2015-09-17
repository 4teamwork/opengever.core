from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
import transaction


class TestProtect(FunctionalTestCase):

    def setUp(self):
        super(TestProtect, self).setUp()
        repo_root = create(Builder('repository_root'))
        repo_folder = create(Builder('repository').within(repo_root))
        self.dossier = create(Builder('dossier').within(repo_folder))
        self.document = create(Builder('document').within(self.dossier))

    @browsing
    def test_initializes_annotations_without_csrf_confirmation(self, browser):
        browser.login().open(self.document)
        self.assertEquals(self.document.absolute_url(), browser.url)

        del self.document.__annotations__
        transaction.commit()

        browser.login().open(self.document)
        self.assertEquals(self.document.absolute_url(), browser.url)
