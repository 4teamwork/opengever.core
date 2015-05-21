from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.testing import FunctionalTestCase


class TestCopyItems(FunctionalTestCase):

    @browsing
    def test_redirects_back_and_show_message_if_no_item_was_selected(self, browser):
        dossier = create(Builder('dossier'))
        browser.login().open(dossier, view='copy_items')

        self.assertEqual(dossier.absolute_url(), browser.url)
        self.assertEqual(['You have not selected any Items.'], error_messages())

    @browsing
    def test_redirects_back_and_show_statusmessage_if_copy_success(self, browser):
        dossier = create(Builder('dossier'))
        doc_a = create(Builder('document').within(dossier))
        doc_b = create(Builder('document').within(dossier))

        paths = ['/'.join(obj.getPhysicalPath()) for obj in [doc_a, doc_b]]
        browser.login().open(dossier, {'paths:list': paths}, view='copy_items')

        self.assertEqual(dossier.absolute_url(), browser.url)
        self.assertEqual(['Selected objects successfully copied.'], info_messages())
