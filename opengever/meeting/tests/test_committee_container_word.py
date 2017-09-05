from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from opengever.testing import IntegrationTestCase
from ftw.testbrowser.pages import factoriesmenu


class TestCommitteeContainer(IntegrationTestCase):

    features = ('meeting', 'word-meeting')

    @browsing
    def test_can_configure_ad_hoc_template(self, browser):
        self.login(self.administrator, browser)
        self.committee_container.ad_hoc_template = None

        self.assertIsNone(self.committee_container.ad_hoc_template)
        self.assertIsNone(self.committee_container.get_ad_hoc_template())

        browser.open(self.committee_container, view='edit')
        browser.fill({'Ad hoc agenda item template': self.proposal_template})
        browser.find('Save').click()

        statusmessages.assert_message('Changes saved')

        self.assertIsNotNone(self.committee_container.ad_hoc_template)
        self.assertEqual(self.proposal_template,
                         self.committee_container.get_ad_hoc_template())

    @browsing
    def test_can_add_with_ad_hoc_template(self, browser):
        self.login(self.manager, browser)
        browser.open()
        factoriesmenu.add('Committee Container')
        browser.fill({'Title': u'Sitzungen',
                      'Protocol template': self.sablon_template,
                      'Excerpt template': self.sablon_template,
                      'Ad hoc agenda item template': self.proposal_template})
        browser.find('Save').click()

        self.assertEqual(self.proposal_template,
                         browser.context.get_ad_hoc_template())
