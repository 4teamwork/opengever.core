from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from opengever.testing import IntegrationTestCase
from operator import methodcaller
from plone.uuid.interfaces import IUUID


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
    def test_visible_fields_in_forms(self, browser):
        """Some fields should only be displayed when the word feature is
        enabled.
        Therefore we test the appearance of all fields.
        """
        fields = ['Title',
                  'Group',
                  'Protocol header template',
                  'Protocol suffix template',
                  'Agendaitem list template',
                  'Table of contents template',
                  'Linked repository folder',
                  'Ad hoc agenda item template',
                  'Paragraph template',
                  'Allowed proposal templates']
        with self.login(self.administrator, browser):
            browser.open(self.committee_container)
            factoriesmenu.add('Committee')
            self.assertEquals(
                fields,
                map(methodcaller('normalized_text', recursive=False),
                    browser.css('form#form > div.field > label')))

        with self.login(self.committee_responsible, browser):
            browser.open(self.committee, view='edit')
            self.assertEquals(
                fields,
                map(methodcaller('normalized_text', recursive=False),
                    browser.css('form#form > div.field > label')))

    @browsing
    def test_configure_allowed_proposal_templates(self, browser):
        with self.login(self.administrator):
            create(Builder('proposaltemplate')
                   .titled(u'Baubewilligung')
                   .within(self.templates))

        self.login(self.committee_responsible, browser)
        self.assertFalse(self.committee.allowed_proposal_templates)

        browser.open(self.committee, view='edit')
        self.assertItemsEqual(
            ['Baubewilligung', u'Geb\xfchren'],
            browser.find('Allowed proposal templates').options)
        browser.fill({'Allowed proposal templates': u'Geb\xfchren'}).save()
        self.assertItemsEqual(
            [IUUID(self.proposal_template)],
            self.committee.allowed_proposal_templates)
