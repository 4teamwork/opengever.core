from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.testing import IntegrationTestCase


class TestRisDossierFactoriesMenu(IntegrationTestCase):

    features = ('ris',)

    @browsing
    def test_proposal_is_visible_in_add_menu(self, browser):
        self.login(self.dossier_responsible, browser)

        browser.open(self.dossier)
        self.assertEqual(
            factoriesmenu.addable_types(),
            [
                'Document',
                'Document from template',
                'Task',
                'Task from template',
                'Subdossier',
                'Participant',
                'Proposal'
            ],
        )

    @browsing
    def test_default_add_factory_redirects_to_ris(self, browser):
        self.login(self.dossier_responsible, browser)

        browser.open(self.dossier)
        add_link = factoriesmenu.menu().find('Proposal')
        self.assertEqual(
            'http://ris.example.com/spv/antrag-erstellen?context={}'.format(
                self.dossier.absolute_url()
            ),
            add_link.get('href'),
        )

    @browsing
    def test_proposal_debug_factory_is_visible_in_add_menu(self, browser):
        self.login(self.manager, browser)

        browser.open(self.dossier)
        self.assertEqual(
            factoriesmenu.addable_types(),
            [
                'Document',
                'Document from template',
                'Task',
                'Task from template',
                'Subdossier',
                'Participant',
                'Proposal',
                'Proposal (Manager: Debug)',
            ],
        )
