from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestDocumentishLayout(FunctionalTestCase):

    def setUp(self):
        super(TestDocumentishLayout, self).setUp()
        self.prepareSession()

        self.repo, self.repo_folder = create(Builder('repository_tree'))

        self.dossier = create(Builder('dossier').within(self.repo_folder))

    @browsing
    def test_removed_documents_body_class_is_suffixed_with_removed_class(self, browser):
        document = create(
            Builder('document').within(self.dossier))
        removed_document = create(
            Builder('document').within(self.dossier).removed())

        browser.login().open(document)
        self.assertNotIn('removed',
                         browser.css('body').first.get('class').split(' '))

        self.grant('Manager')
        browser.login().open(removed_document)
        self.assertIn('removed',
                      browser.css('body').first.get('class').split(' '))

    @browsing
    def test_mail_documents_body_class_is_suffixed_with_removed_class(self, browser):
        mail = create(Builder('mail').within(self.dossier))
        removed_mail = create(Builder('mail').within(self.dossier).removed())
        self.grant('Manager')

        browser.login().open(mail)
        self.assertNotIn('removed',
                         browser.css('body').first.get('class').split(' '))

        self.grant('Manager')
        browser.login().open(removed_mail)
        self.assertIn('removed',
                      browser.css('body').first.get('class').split(' '))
