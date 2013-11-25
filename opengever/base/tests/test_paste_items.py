from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase


class TestPasteItems(FunctionalTestCase):

    use_browser = True

    def setUp(self):
        super(TestPasteItems, self).setUp()
        self.grant('Manager')

    def test_paste_action_not_displayed_for_contactfolder(self):
        contactfolder = create(Builder('contactfolder'))
        contact = create(Builder('contact')
                         .within(contactfolder))

        contactfolder.manage_copyObjects(contact.id)

        self.browser.open(contactfolder.absolute_url())
        self.assertNotIn('actionicon-object_buttons-paste',
                         self.browser.contents)

    def test_paste_action_not_displayed_for_templatedossier(self):
        templatedossier = create(Builder('templatedossier'))
        document = create(Builder('document')
                         .within(templatedossier))

        templatedossier.manage_copyObjects(document.id)

        self.browser.open(templatedossier.absolute_url())
        self.assertNotIn('actionicon-object_buttons-paste',
                         self.browser.contents)

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
