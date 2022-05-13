from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.document.interfaces import ITemplateDocumentMarker
from opengever.testing import IntegrationTestCase


class TestTemplateDocument(IntegrationTestCase):

    @browsing
    def test_document_is_marked_as_template_when_added_in_template_folder(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.templates)

        with self.observe_children(self.templates) as children:
            factoriesmenu.add('Document')
            browser.fill({'Title': u'My Document'}).save()

        self.assertEqual(1, len(children["added"]))
        doc = children["added"].pop()
        self.assertTrue(ITemplateDocumentMarker.providedBy(doc))

    @browsing
    def test_document_is_not_marked_as_template_when_added_in_template_dossier(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossiertemplate)

        with self.observe_children(self.dossiertemplate) as children:
            factoriesmenu.add('Document')
            browser.fill({'Title': u'My Document'}).save()

        self.assertEqual(1, len(children["added"]))
        doc = children["added"].pop()
        self.assertFalse(ITemplateDocumentMarker.providedBy(doc))
