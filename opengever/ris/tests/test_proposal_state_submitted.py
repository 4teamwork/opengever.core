from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from opengever.testing import IntegrationTestCase


class TestRisProposalStateSubmitted(IntegrationTestCase):

    features = ('ris',)

    def setUp(self):
        super(TestRisProposalStateSubmitted, self).setUp()
        with self.login(self.manager):
            self.ris_proposal = create(
                Builder('ris_proposal')
                .within(self.dossier)
                .having(document=self.document)
                .in_state('proposal-state-submitted')
            )

    @browsing
    def test_visible_actions_for_dossier_responsible(self, browser):
        self.login(self.dossier_responsible, browser)

        browser.open(self.ris_proposal)
        # Somehow the `Actions` menu is completely invisible
        self.assertEqual(editbar.menu_options('Actions'), [])

    @browsing
    def test_visible_actions_for_manager(self, browser):
        self.login(self.manager, browser)

        browser.open(self.ris_proposal)
        self.assertEqual(
            editbar.menu_options('Actions'),
            [
                'Sharing',
                'Reject (Manager: Debug)',
                'Schedule (Manager: Debug)',
                'Policy...',
            ]
        )
