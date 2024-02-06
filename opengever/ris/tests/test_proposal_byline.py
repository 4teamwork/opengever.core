from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.tests.byline_base_test import TestBylineBase


class TestRisProposalByline(TestBylineBase):

    features = ('ris',)

    def setUp(self):
        super(TestRisProposalByline, self).setUp()
        with self.login(self.manager):
            self.ris_proposal = create(
                Builder('ris_proposal')
                .within(self.dossier)
                .having(document=self.document)
            )

    @browsing
    def test_proposal_byline_issuer_display(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        browser.open(self.ris_proposal)

        responsible = self.get_byline_value_by_label('Issuer:')
        self.assertEquals('test_user_1_ (test-user)', responsible.text)

    @browsing
    def test_proposal_byline_state_display(self, browser):
        self.login(self.dossier_responsible, browser=browser)
        browser.open(self.ris_proposal)

        state = self.get_byline_value_by_label('State:')
        self.assertEquals('Active', state.text)
