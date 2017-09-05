from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.testing import IntegrationTestCase


class TestCommitteeWord(IntegrationTestCase):

    features = ('meeting', 'word-meeting')

    @browsing
    def test_can_configure_ad_hoc_template(self, browser):
        self.login(self.committee_responsible, browser)

        self.assertIsNone(self.committee.ad_hoc_template)

        browser.open(self.committee, view='edit')
        browser.fill({'Ad hoc agenda item template': self.proposal_template})
        browser.find('Save').click()

        statusmessages.assert_message('Changes saved')

        self.assertIsNotNone(self.committee.ad_hoc_template)
        self.assertEqual(self.proposal_template,
                         self.committee.get_ad_hoc_template())

    def test_get_ad_hoc_template_returns_committee_template_if_available(self):
        self.login(self.committee_responsible)
        self.committee.ad_hoc_template = self.as_relation_value(
            self.proposal_template)

        self.assertEqual(
            self.proposal_template, self.committee.get_ad_hoc_template())

    def test_get_ad_hoc_template_falls_back_to_container(self):
        self.login(self.administrator)
        self.committee_container.ad_hoc_template = self.as_relation_value(
            self.proposal_template)

        self.assertIsNone(self.committee.ad_hoc_template)
        self.assertEqual(
            self.proposal_template, self.committee.get_ad_hoc_template())
