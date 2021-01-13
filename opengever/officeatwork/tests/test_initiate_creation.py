from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.core.testing import OPENGEVER_FUNCTIONAL_OFFICEATWORK_LAYER
from opengever.testing import FunctionalTestCase
from plone import api


class TestInitiateCreationWithOfficeatwork(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_OFFICEATWORK_LAYER

    def setUp(self):
        super(TestInitiateCreationWithOfficeatwork, self).setUp()
        self.dossier = create(Builder('dossier'))

    @browsing
    def test_creation_initiated_with_officeatwork_creates_shadow_doc(self, browser):
        browser.login().open(self.dossier.absolute_url())
        factoriesmenu.add('Document from officeatwork')
        # No file, not preserved as paper, validator is skipped on purpose
        browser.fill({'Title': 'A doc'})
        browser.find('Create with officeatwork').click()

        self.assertEqual(
            ['Creation with officeatwork initiated successfully'],
            info_messages())
        shadow_doc = self.dossier.restrictedTraverse('document-1', None)
        self.assertIsNotNone(shadow_doc)

        self.assertEqual('document-state-shadow',
                         api.content.get_state(shadow_doc))
        self.assertTrue(shadow_doc.is_shadow_document())
