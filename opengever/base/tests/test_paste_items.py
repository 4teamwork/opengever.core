from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestPasteItems(FunctionalTestCase):

    def setUp(self):
        super(TestPasteItems, self).setUp()
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
        self.assertSequenceEqual(['Sharing'], actions)

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
        self.assertSequenceEqual(['Properties', 'Sharing'], actions)

    @browsing
    def test_paste_action_not_displayed_for_mails(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))
        mail = create(Builder('mail').within(dossier))

        paths = ['/'.join(document.getPhysicalPath())]
        browser.login().open(dossier, {'paths:list': paths}, view='copy_items')

        browser.open(mail)
        actions = browser.css('#plone-contentmenu-actions li').text
        self.assertSequenceEqual(['Properties', 'save attachments'], actions)

    def test_pasting_copied_document_into_dossier_succeeds(self):
        dossier = create(Builder('dossier'))
        document = create(Builder('document')
                          .within(dossier))

        cb = dossier.manage_copyObjects(document.id)
        dossier.manage_pasteObjects(cb)
        self.assertIn("copy_of_%s" % document.id, dossier.objectIds())

    def test_pasting_copied_dossier_into_repository_folder_succeeds(self):
        repofolder = create(Builder('repository'))
        dossier = create(Builder('dossier')
                         .within(repofolder))

        cb = repofolder.manage_copyObjects(dossier.id)
        repofolder.manage_pasteObjects(cb)
        self.assertIn("copy_of_%s" % dossier.id, repofolder.objectIds())

    def test_pasting_dossier_with_docs_into_repository_folder_succeeds(self):
        repofolder = create(Builder('repository'))
        dossier = create(Builder('dossier')
                         .within(repofolder))
        document = create(Builder('document')
                          .within(dossier))

        cb = repofolder.manage_copyObjects(dossier.id)
        repofolder.manage_pasteObjects(cb)

        copied_dossier_id = "copy_of_%s" % dossier.id

        self.assertIn(copied_dossier_id, repofolder.objectIds())
        self.assertIn(document.id, repofolder["copy_of_%s" % dossier.id])

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
