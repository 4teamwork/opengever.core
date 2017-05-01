from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_OFFICEATWORK_LAYER
from opengever.testing import FunctionalTestCase


class TestShadowState(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_OFFICEATWORK_LAYER

    def setUp(self):
        super(TestShadowState, self).setUp()
        self.dossier = create(Builder('dossier'))
        self.document = create(Builder('document')
                               .within(self.dossier)
                               .as_shadow_document())

    @browsing
    def test_document_in_shadow_state_is_visible_for_owner(self, browser):
        browser.login().open(self.document)
        self.assertTrue(browser.context.is_shadow_document())

    @browsing
    def test_document_in_shadow_state_is_invisible_for_other_users(self, browser):
        user = create(Builder('user').with_roles(
            'Reader', 'Contributor', 'Editor', 'Reviewer', 'Publisher'))

        with browser.expect_unauthorized():
            browser.login(user.getId()).visit(self.document)
