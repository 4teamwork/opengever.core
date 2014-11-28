from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestDocumentishLayout(FunctionalTestCase):

    def setUp(self):
        super(TestDocumentishLayout, self).setUp()

        self.grant('Manager')

    @browsing
    def test_removed_documents_body_class_is_suffixed_with_removed_class(self, browser):
        document = create(Builder('document'))
        removed_document = create(Builder('document').removed())

        browser.login().open(document)
        self.assertEquals(
            'template-tabbed_view portaltype-opengever-document-document site-plone section-document-1 icons-on',
            browser.css('body').first.get('class'))

        browser.login().open(removed_document)
        self.assertEquals(
            'template-tabbed_view portaltype-opengever-document-document site-plone section-document-2 icons-on removed',
            browser.css('body').first.get('class'))

    @browsing
    def test_mail_documents_body_class_is_suffixed_with_removed_class(self, browser):
        mail = create(Builder('mail'))
        removed_mail = create(Builder('mail').removed())

        default_class = 'template-tabbed_view portaltype-ftw-mail-mail site-plone section-document-1 icons-on'

        browser.login().open(mail)
        self.assertEquals(
            'template-tabbed_view portaltype-ftw-mail-mail site-plone section-document-1 icons-on',
            browser.css('body').first.get('class'))

        browser.login().open(removed_mail)
        self.assertEquals(
            'template-tabbed_view portaltype-ftw-mail-mail site-plone section-document-2 icons-on removed',
            browser.css('body').first.get('class'))
