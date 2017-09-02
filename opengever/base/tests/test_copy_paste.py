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


class TestCopyItem(FunctionalTestCase):

    def setUp(self):
        super(TestCopyItem, self).setUp()
        self.repo, self.repo_folder = create(Builder('repository_tree'))
        self.dossier = create(Builder('dossier')
                              .within(self.repo_folder))
        self.document = create(Builder('document')
                               .within(self.dossier))
        self.mail = create(Builder('mail')
                           .within(self.dossier))

    @browsing
    def test_statusmessage_if_copy_document_success(self, browser):
        browser.login().open(self.document, view='copy_item')

        self.assertEqual(self.document.absolute_url(), browser.url)
        self.assertEqual(['Selected objects successfully copied.'],
                         info_messages())

    @browsing
    def test_statusmessage_if_paste_document_success(self, browser):
        browser.login().open(self.document, view='copy_item')
        dest_dossier = create(Builder('dossier'))

        browser.open(dest_dossier, view='tabbed_view')
        browser.css('#contentActionMenus a#paste').first.click()

        self.assertEqual(dest_dossier.absolute_url(), browser.url)
        self.assertEqual(['Objects from clipboard successfully pasted.'],
                         info_messages())

    @browsing
    def test_statusmessage_if_copy_mail_success(self, browser):
        browser.login().open(self.mail, view='copy_item')

        self.assertEqual(self.mail.absolute_url(), browser.url)
        self.assertEqual(['Selected objects successfully copied.'],
                         info_messages())

    @browsing
    def test_statusmessage_if_paste_mail_success(self, browser):
        browser.login().open(self.mail, view='copy_item')
        dest_dossier = create(Builder('dossier'))

        browser.open(dest_dossier, view='tabbed_view')
        browser.css('#contentActionMenus a#paste').first.click()

        self.assertEqual(dest_dossier.absolute_url(), browser.url)
        self.assertEqual(['Objects from clipboard successfully pasted.'],
                         info_messages())


class TestCopyPaste(FunctionalTestCase):

    def setUp(self):
        super(TestCopyPaste, self).setUp()
        self.grant('Reader', 'Contributor', 'Editor')

    @browsing
    def test_pasting_empty_clipboard_shows_message_and_redirect_back(self, browser):
        dossier = create(Builder('dossier'))
        browser.login().open(dossier, view='paste_clipboard')

        self.assertEqual(dossier.absolute_url(), browser.url)
        self.assertEqual([u"Can't paste items; the clipboard is emtpy"],
                         error_messages())

    @browsing
    def test_creates_objects_with_correct_id_format(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        paths = ['/'.join(document.getPhysicalPath())]
        browser.login().open(dossier, view="copy_items", data={'paths:list': paths})
        browser.css('#contentActionMenus a#paste').first.click()

        copy = dossier.getFolderContents()[-1]
        self.assertEquals('document-2', copy.getId)

    @browsing
    def test_pasting_handles_multiple_items_in_clipboard(self, browser):
        dossier = create(Builder('dossier'))
        document_a = create(Builder('document').within(dossier))
        document_b = create(Builder('document').within(dossier))

        paths = ['/'.join(obj.getPhysicalPath()) for obj in [document_a, document_b]]
        browser.login().open(dossier, view="copy_items", data={'paths:list': paths})
        browser.css('#contentActionMenus a#paste').first.click()

        self.assertEquals(4, len(dossier.getFolderContents()))

    @browsing
    def test_id_of_nested_objects_have_correct_format(self, browser):
        dossier_a = create(Builder('dossier'))
        dossier_b = create(Builder('dossier'))
        subdossier = create(Builder('dossier').within(dossier_a))
        create(Builder('document').within(subdossier))

        paths = ['/'.join(subdossier.getPhysicalPath())]
        browser.login().open(dossier_a, view="copy_items", data={'paths:list': paths})
        browser.open(dossier_b)
        browser.css('#contentActionMenus a#paste').first.click()

        subdossier_copy = dossier_b.get('dossier-4')
        document_copy = subdossier_copy.listFolderContents()[0]
        self.assertEquals('document-2', document_copy.id)

    @browsing
    def test_copy_document_into_dossier_succeeds(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))

        browser.login().open(
            dossier, view="copy_items",
            data={'paths:list': ['/'.join(document.getPhysicalPath())]})
        browser.css('#contentActionMenus a#paste').first.click()

        self.assertEqual(2, len(dossier.getFolderContents()))
        self.assertEqual(["Objects from clipboard successfully pasted."],
                         info_messages())

    @browsing
    def test_pasting_copied_dossier_into_repository_folder_succeeds(self, browser):
        repofolder = create(Builder('repository'))
        dossier = create(Builder('dossier')
                         .within(repofolder))

        browser.login().open(
            repofolder, view="copy_items",
            data={'paths:list': ['/'.join(dossier.getPhysicalPath())]})
        browser.css('#contentActionMenus a#paste').first.click()

        self.assertEqual(2, len(repofolder.getFolderContents()))

    @browsing
    def test_pasting_dossier_with_docs_into_repository_folder_succeeds(self, browser):
        repofolder_1 = create(Builder('repository'))
        repofolder_2 = create(Builder('repository'))
        dossier = create(Builder('dossier').within(repofolder_1))
        create(Builder('document').within(dossier))

        browser.login().open(
            repofolder_2, view="copy_items",
            data={'paths:list': ['/'.join(dossier.getPhysicalPath())]})
        browser.css('#contentActionMenus a#paste').first.click()

        dossiers = repofolder_2.listFolderContents()
        self.assertEqual(1, len(dossiers))
        self.assertEqual(1, len(dossiers[0].listFolderContents()))

    @browsing
    def test_object_renaming_is_not_journalized(self, browser):
        """When a object gets copied, it has to be renamed after the creation,
        to use the correct format, but this shouldn't add additional journal
        entries.
        """
        repo_1 = create(Builder('repository'))
        repo_2 = create(Builder('repository'))
        dossier = create(Builder('dossier').within(repo_1))
        create(Builder('document').within(dossier))

        paths = {'paths:list': ['/'.join(dossier.getPhysicalPath())]}
        browser.login().open(repo_2, view="copy_items", data=paths)
        browser.css('#contentActionMenus a#paste').first.click()

        copy = repo_2.listFolderContents()[-1]

        browser.open(copy, view='tabbedview_view-journal')
        listing = browser.css('.listing').first
        titles = [row.get('Title') for row in listing.dicts()]

        self.assertNotIn(u'Object moved: copy of Testdokum\xe4nt',
                         titles, '"Object moved" unexpectedly journalized')
        self.assertNotIn(u'Object cut: copy of Testdokum\xe4nt', titles,
                         '"Object cut" unexpectedly journalized')

        self.assertEqual(['Dossier modified: dossier-2',
                          'Dossier added: dossier-1',
                          u'Document added: copy of Testdokum\xe4nt',
                          'Dossier modified: dossier-1',
                          u'Document added: Testdokum\xe4nt',
                          'Dossier added: dossier-1'], titles)

    @browsing
    def test_pasting_dossiers_into_a_branch_node_redirects_back_and_shows_statusmessage(self, browser):
        branch_node = create(Builder('repository'))
        leaf_node = create(Builder('repository').within(branch_node))
        dossier = create(Builder('dossier').within(leaf_node))

        browser.login().open(
            leaf_node, view="copy_items",
            data={'paths:list': ['/'.join(dossier.getPhysicalPath())]})

        browser.login().open(branch_node)
        browser.click_on('Paste')

        self.assertEqual(
            ["Can't paste items, it's not allowed to add objects of this type."],
            error_messages())
        self.assertEqual(branch_node.absolute_url(), browser.url)

    @browsing
    def test_copy_document_from_repository_into_private_folder_fails(self, browser):  # noqa
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))
        private_dossier = create(Builder('private_dossier'))

        browser.login().open(
            dossier, view="copy_items",
            data={'paths:list': ['/'.join(document.getPhysicalPath())]})
        browser.css('#contentActionMenus a#paste').first.click()

        browser.open(private_dossier, view='paste_clipboard')
        self.assertEqual(
            ["Can't paste items, the context does not allow pasting items."],
            error_messages())
