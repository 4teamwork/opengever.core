from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
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

    @browsing
    def test_can_configure_paragraph_template(self, browser):
        self.login(self.committee_responsible, browser)
        self.committee_container.paragraph_template = None
        self.committee.paragraph_template = None

        browser.open(self.committee, view='edit')
        browser.fill({'Paragraph template': self.sablon_template}).save()
        statusmessages.assert_message('Changes saved')

        self.assertIsNotNone(self.committee.paragraph_template)
        self.assertEqual(self.sablon_template,
                         self.committee.get_paragraph_template())

    def test_get_paragraph_template_returns_committee_template_if_available(self):
        self.login(self.committee_responsible)
        self.committee.paragraph_template = self.as_relation_value(self.sablon_template)
        self.committee_container.paragraph_template = None
        self.assertEqual(self.sablon_template, self.committee.get_paragraph_template())

    def test_get_paragraph_template_falls_back_to_container(self):
        self.login(self.administrator)
        self.committee.paragraph_template = None
        self.committee_container.paragraph_template = self.as_relation_value(
            self.sablon_template)
        self.assertEqual(self.sablon_template, self.committee.get_paragraph_template())

    @browsing
    def test_hide_paragraph_template_for_nonword_in_add_form(self, browser):
        """The "Paragraph template" field only makes sense when
        the word-meeting feature is enabled.
        Make sure that it does not appear in the forms when disabling
        the word-meeting feature.
        """
        self.login(self.manager, browser)
        browser.open(self.committee_container)
        factoriesmenu.add('Committee')
        field_label = 'Paragraph template'
        self.assertTrue(browser.find(field_label))

        self.deactivate_feature('word-meeting')
        browser.reload()
        self.assertFalse(browser.find(field_label))

    @browsing
    def test_hide_paragraph_template_for_nonword_in_edit_form(self, browser):
        """The "Paragraph template" field only makes sense when
        the word-meeting feature is enabled.
        Make sure that it does not appear in the forms when disabling
        the word-meeting feature.
        """
        self.login(self.manager, browser)
        browser.open(self.committee, view='edit')
        field_label = 'Paragraph template'
        self.assertTrue(browser.find(field_label))

        self.deactivate_feature('word-meeting')
        browser.reload()
        self.assertFalse(browser.find(field_label))
