from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.testing import FunctionalTestCase


class TestPastingAllowed(FunctionalTestCase):

    def setUp(self):
        super(TestPastingAllowed, self).setUp()
        self.grant('Manager')

    @browsing
    def test_paste_action_not_displayed_for_contactfolder(self, browser):
        contactfolder = create(Builder('contactfolder'))
        contact = create(Builder('contact')
                         .within(contactfolder))

        paths = ['/'.join(contact.getPhysicalPath())]
        browser.login().open(contactfolder, {'paths:list': paths},
                             view='copy_items')

        browser.open(contactfolder)
        actions = browser.css('#plone-contentmenu-actions li').text
        self.assertSequenceEqual(['Export as Zip', 'Sharing'], actions)

    @browsing
    def test_paste_action_not_displayed_for_templatedossier(self, browser):
        templatedossier = create(Builder('templatedossier'))
        document = create(Builder('document')
                          .within(templatedossier))

        paths = ['/'.join(document.getPhysicalPath())]
        browser.login().open(templatedossier, {'paths:list': paths},
                             view='copy_items')

        browser.open(templatedossier)
        actions = browser.css('#plone-contentmenu-actions li').text
        self.assertSequenceEqual(
            ['Export as Zip', 'Properties', 'Sharing'], actions)

    @browsing
    def test_paste_action_not_displayed_for_mails(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))
        mail = create(Builder('mail').within(dossier))

        paths = ['/'.join(document.getPhysicalPath())]
        browser.login().open(dossier, {'paths:list': paths}, view='copy_items')

        browser.open(mail)
        actions = browser.css('#plone-contentmenu-actions li').text
        self.assertSequenceEqual(
            ['Export as Zip', 'Properties', 'save attachments'], actions)

    def test_pasting_not_allowed_if_disallowed_subobject_type(self):
        repofolder = create(Builder('repository'))
        dossier = create(Builder('dossier')
                         .within(repofolder))
        document = create(Builder('document')
                          .within(dossier))

        dossier.manage_copyObjects(document.id)
        pasting_allowed_view = repofolder.restrictedTraverse(
            'is_pasting_allowed')
        allowed = pasting_allowed_view()
        self.assertFalse(allowed)


class TestCopyPaste(FunctionalTestCase):

    def setUp(self):
        super(TestCopyPaste, self).setUp()
        self.grant('Reader', 'Contributor', 'Editor')

    @browsing
    def test_pasting_empty_clipboard_shows_message_and_redirect_back(self, browser):
        dossier = create(Builder('dossier'))
        browser.login().open(dossier, view='paste_clipboard')

        self.assertEqual(dossier.absolute_url(), browser.url)
        self.assertEqual([u"Can't paste items, the clipboard is emtpy"],
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
