from ftw.testbrowser import browsing
from opengever.docugate.interfaces import IDocumentFromDocugate
from opengever.testing import IntegrationTestCase
from zope.interface import alsoProvides


class TestRetryWithDocugateAction(IntegrationTestCase):

    features = ("officeconnector-checkout", "docugate")

    @browsing
    def test_docugate_retry_action_is_available(self, browser):
        self.login(self.dossier_responsible, browser)
        alsoProvides(self.shadow_document, IDocumentFromDocugate)
        browser.open(self.shadow_document,
                     view='tabbed_view/listing?view_name=overview')
        action = browser.find_link_by_text('Retry with Docugate')
        self.assertTrue(action is not None)

    @browsing
    def test_docugate_retry_action_is_not_available(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.open(self.shadow_document,
                     view='tabbed_view/listing?view_name=overview')
        action = browser.find_link_by_text('Retry with Docugate')
        self.assertTrue(action is None)

        browser.open(self.document,
                     view='tabbed_view/listing?view_name=overview')
        action = browser.find_link_by_text('Retry with Docugate')
        self.assertTrue(action is None)
