from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ZSERVER_TESTING
from opengever.testing import FunctionalTestCase
from opengever.testing.officeconnector import TestOfficeConnector
from plone import api
import transaction


class TestWebDAVUnlock(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ZSERVER_TESTING

    def setUp(self):
        super(TestWebDAVUnlock, self).setUp()
        self.dossier = create(Builder('dossier'))
        self.document = create(Builder('document')
                               .within(self.dossier)
                               .checked_out()
                               .as_shadow_document())

    @browsing
    def test_unlocking_documents_exits_shadow_state(self, browser):
        browser.login()
        connector = TestOfficeConnector(self.document, browser)
        connector.lock()
        connector.unlock()

        browser.open(self.document)
        transaction.begin()
        self.assertFalse(browser.context.is_shadow_document())
        self.assertEqual('document-state-draft',
                         api.content.get_state(browser.context))

    @browsing
    def test_unlocking_document_is_visible_for_other_users(self, browser):
        browser.login()
        connector = TestOfficeConnector(self.document, browser)
        connector.lock()
        connector.unlock()

        user = create(Builder('user').with_roles(
            'Reader', 'Contributor', 'Editor', 'Reviewer', 'Publisher'))
        browser.login(user.getId()).visit(self.document)
        self.assertEqual(self.document, browser.context)
