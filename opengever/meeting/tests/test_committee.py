from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import dexterity
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from opengever.base.oguid import Oguid
from opengever.meeting.model import Committee
from opengever.testing import IntegrationTestCase
from operator import methodcaller
from plone.uuid.interfaces import IUUID


class TestCommittee(IntegrationTestCase):

    features = ('meeting',)

    group_field_name = 'Committeeresponsible'
    maxDiff = None

    def test_committee_id_is_generated(self):
        self.login(self.administrator)
        self.assertEqual('committee-1', self.committee.getId())

    def test_committee_model_is_initialized_correctly(self):
        self.login(self.administrator)
        model = self.committee.load_model()

        self.assertIsNotNone(model)
        self.assertEqual(Oguid.for_object(self.committee), model.oguid)

    def test_get_toc_template_returns_committee_template_if_available(self):
        self.login(self.administrator)
        self.committee.toc_template = self.as_relation_value(
            self.sablon_template)

        self.assertEqual(
            self.sablon_template, self.committee.get_toc_template())

    def test_get_toc_template_falls_back_to_container(self):
        self.login(self.administrator)
        self.committee_container.toc_template = self.as_relation_value(
            self.sablon_template)

        self.assertIsNone(self.committee.toc_template)
        self.assertEqual(
            self.sablon_template, self.committee.get_toc_template())

    def test_get_protocol_header_template_returns_committee_template_if_available(self):
        self.login(self.administrator)
        self.activate_feature('meeting')
        self.committee.protocol_header_template = self.as_relation_value(
            self.sablon_template)

        self.assertEqual(
            self.sablon_template, self.committee.get_protocol_header_template())

    def test_get_protocol_header_template_falls_back_to_container(self):
        self.login(self.administrator)
        self.activate_feature('meeting')
        self.assertIsNone(self.committee.protocol_header_template)
        self.assertIsNotNone(self.committee_container.protocol_header_template)

        self.assertEqual(
            self.sablon_template, self.committee.get_protocol_header_template())

    def test_get_protocol_suffix_template_returns_committee_template_if_available(self):
        self.login(self.administrator)
        self.activate_feature('meeting')
        self.committee.protocol_suffix_template = self.as_relation_value(
            self.sablon_template)

        self.assertEqual(
            self.sablon_template, self.committee.get_protocol_suffix_template())

    def test_get_protocol_suffix_template_falls_back_to_container_if_available(self):
        self.login(self.administrator)
        self.activate_feature('meeting')
        self.committee_container.protocol_suffix_template = self.as_relation_value(
            self.sablon_template)

        self.assertIsNone(self.committee.protocol_suffix_template)
        self.assertIsNotNone(self.committee_container.protocol_suffix_template)

        self.assertEqual(
            self.sablon_template, self.committee.get_protocol_suffix_template())

    @browsing
    def test_committee_edit_form_fieldsets(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.committee, view='edit')
        form = browser.forms["form"]

        self.assertEqual(1, len(form.css("#fieldset-default")))
        fieldset = form.css("#fieldset-default")
        self.assertEqual('Default', fieldset.css("legend").first.text)

        self.assertEqual(1, len(form.css("#fieldset-0")))
        fieldset = form.css("#fieldset-0")
        self.assertEqual('Protocol templates', fieldset.css("legend").first.text)

        self.assertEqual(1, len(form.css("#fieldset-1")))
        fieldset = form.css("#fieldset-1")
        self.assertEqual('Excerpt templates', fieldset.css("legend").first.text)

    @browsing
    def test_can_configure_ad_hoc_template(self, browser):
        self.login(self.committee_responsible, browser)

        self.committee.ad_hoc_template = None

        browser.open(self.committee, view='edit')
        browser.fill({'Ad hoc agenda item template': self.proposal_template})
        browser.find('Save').click()

        statusmessages.assert_message('Changes saved')

        self.assertIsNotNone(self.committee.ad_hoc_template)
        self.assertEqual(self.proposal_template,
                         self.committee.get_ad_hoc_template())

    @browsing
    def test_not_allowed_default_ad_hoc_template_is_rejected(self, browser):
        self.login(self.committee_responsible, browser)

        browser.open(self.committee, view='edit')
        browser.fill({'Allowed ad-hoc agenda item templates': u'Freitext Traktandum'})
        browser.fill({'Ad hoc agenda item template': self.proposal_template})

        browser.find('Save').click()
        self.assertItemsEqual(['There were some errors.'],
                              statusmessages.error_messages())

        invariance_errors = browser.css('#content-core div div div.error').text
        self.assertItemsEqual(
            [u'The default ad-hoc agenda item template has to be amongst the '
             u'allowed ones for this committee.'],
            invariance_errors)

    def test_get_ad_hoc_template_returns_committee_template_if_available(self):
        self.login(self.committee_responsible)
        self.committee.ad_hoc_template = self.as_relation_value(
            self.proposal_template)

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

    def test_get_agenda_item_header_template_falls_back_to_container(self):
        self.login(self.administrator)
        self.committee_container.agenda_item_header_template = self.as_relation_value(
            self.sablon_template)
        self.assertIsNone(self.committee.agenda_item_header_template)

        self.assertEqual(
            self.sablon_template,
            self.committee.get_excerpt_header_template())

    def test_get_agenda_item_header_template_returns_committee_template_if_available(self):
        self.login(self.administrator)
        self.committee.agenda_item_header_template = self.as_relation_value(
            self.sablon_template)

        self.assertEqual(
            self.sablon_template, self.committee.get_agenda_item_header_template())

    def test_get_agenda_item_suffix_template_falls_back_to_container(self):
        self.login(self.administrator)
        self.committee_container.agenda_item_suffix_template = self.as_relation_value(
            self.sablon_template)
        self.assertIsNone(self.committee.agenda_item_suffix_template)

        self.assertEqual(
            self.sablon_template,
            self.committee.get_excerpt_suffix_template())

    def test_get_agenda_item_suffix_template_returns_committee_template_if_available(self):
        self.login(self.administrator)
        self.committee.agenda_item_suffix_template = self.as_relation_value(
            self.sablon_template)

        self.assertEqual(
            self.sablon_template, self.committee.get_agenda_item_suffix_template())

    def test_get_excerpt_header_template_falls_back_to_container(self):
        self.login(self.administrator)
        self.assertIsNone(self.committee.excerpt_header_template)
        self.assertIsNotNone(self.committee_container.excerpt_header_template)

        self.assertEqual(
            self.sablon_template, self.committee.get_excerpt_header_template())

    def test_get_excerpt_header_template_returns_committee_template_if_available(self):
        self.login(self.administrator)
        self.committee.excerpt_header_template = self.as_relation_value(
            self.sablon_template)

        self.assertEqual(
            self.sablon_template, self.committee.get_excerpt_header_template())

    def test_get_excerpt_suffix_template_falls_back_to_container(self):
        self.login(self.administrator)
        self.assertIsNone(self.committee.excerpt_suffix_template)
        self.assertIsNotNone(self.committee_container.excerpt_suffix_template)

        self.assertEqual(
            self.sablon_template, self.committee.get_excerpt_suffix_template())

    def test_get_excerpt_suffix_template_returns_committee_template_if_available(self):
        self.login(self.administrator)
        self.committee.excerpt_suffix_template = self.as_relation_value(
            self.sablon_template)

        self.assertEqual(
            self.sablon_template, self.committee.get_excerpt_suffix_template())

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
            [
                'Baubewilligung',
                u'Geb\xfchren',
                u'Freitext Traktandum',
                u'Wiederkehrendes Traktandum',
            ],
            browser.find('Allowed proposal templates').options)
        browser.fill({'Allowed proposal templates': u'Geb\xfchren'}).save()
        self.assertItemsEqual(
            [IUUID(self.proposal_template)],
            self.committee.allowed_proposal_templates)

    @browsing
    def test_committee_repository_is_validated(self, browser):
        self.login(self.administrator, browser)

        browser.open(self.committee_container,
                     view='++add++opengever.meeting.committee')

        browser.fill(
            {'Title': u'A c\xf6mmittee',
             'Linked repository folder': self.branch_repofolder,
             self.group_field_name: 'committee_rpk_group'})
        browser.css('#form-buttons-save').first.click()

        self.assertEqual(
            'You cannot add dossiers in the selected repository folder. '
            'Either you do not have the privileges or the repository folder '
            'contains another repository folder.',
            dexterity.erroneous_fields()['Linked repository folder'][0])

    @browsing
    def test_committee_can_be_created_in_browser(self, browser):
        self.login(self.administrator, browser)

        browser.open(self.committee_container,
                     view='++add++opengever.meeting.committee')

        browser.fill(
            {'Title': u'A c\xf6mmittee',
             'Protocol header template': self.sablon_template,
             'Protocol suffix template': self.sablon_template,
             'Excerpt header template': self.sablon_template,
             'Table of contents template': self.sablon_template,
             'Linked repository folder': self.leaf_repofolder,
             self.group_field_name: 'committee_rpk_group'})
        browser.css('#form-buttons-save').first.click()

        browser.fill({'Title': u'Initial',
                      'Start date': '01.01.2012',
                      'End date': '31.12.2012'}).submit()

        statusmessages.assert_message('Item created')

        committee = browser.context
        self.assertEqual('committee-3', committee.getId())
        self.assertEqual(
            ('CommitteeResponsible',),
            dict(committee.get_local_roles()).get('committee_rpk_group'))
        self.assertEqual(self.leaf_repofolder,
                         committee.get_repository_folder())
        self.assertEqual(self.sablon_template,
                         committee.get_toc_template())

        model = committee.load_model()
        self.assertIsNotNone(model)
        self.assertEqual(Oguid.for_object(committee), model.oguid)
        self.assertEqual(u'A c\xf6mmittee', model.title)

        self.assertEqual(1, len(model.periods))
        period = model.periods[0]
        self.assertEqual('active', period.workflow_state)
        self.assertEqual(u'Initial', period.title)
        self.assertEqual(date(2012, 1, 1), period.date_from)
        self.assertEqual(date(2012, 12, 31), period.date_to)

    @browsing
    def test_committee_can_be_edited_in_browser(self, browser):
        self.login(self.committee_responsible, browser)

        local_roles = dict(self.committee.get_local_roles())
        self.assertIn('committee_rpk_group', local_roles)
        self.assertNotIn('committee_ver_group', local_roles)

        browser.open(self.committee, view='edit')
        form = browser.forms['form']

        self.assertEqual(u'Rechnungspr\xfcfungskommission',
                         form.find_field('Title').value)

        browser.fill({'Title': u'A c\xf6mmittee',
                      self.group_field_name: u'committee_ver_group'})
        browser.css('#form-buttons-save').first.click()

        statusmessages.assert_message('Changes saved')

        committee = browser.context
        local_roles = dict(committee.get_local_roles())
        self.assertEqual('committee-1', committee.getId())
        self.assertNotIn('committee_rpk_group', local_roles,)
        self.assertEqual(('CommitteeResponsible',),
                         local_roles.get('committee_ver_group'))

        model = committee.load_model()
        self.assertIsNotNone(model)
        self.assertEqual(u'A c\xf6mmittee', model.title)

        browser.open(self.committee, view='edit')
        self.assertEqual(
            'committee_ver_group', browser.find('Committeeresponsible').value)


class TestCommitteeWorkflow(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_active_committee_can_be_deactivated(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.empty_committee)

        editbar.menu_option('Actions', 'deactivate').click()

        self.assertEqual(Committee.STATE_INACTIVE,
                         self.empty_committee.load_model().get_state())
        statusmessages.assert_message('Committee deactivated successfully')

    def test_initial_state_is_active(self):
        self.login(self.committee_responsible)
        self.assertEqual(Committee.STATE_ACTIVE,
                         self.empty_committee.load_model().get_state())

    @browsing
    def test_deactivating_is_not_possible_when_pending_meetings_exists(
            self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.committee)

        editbar.menu_option('Actions', 'deactivate').click()

        self.assertEqual(Committee.STATE_ACTIVE,
                         self.committee.load_model().get_state())
        statusmessages.assert_message('Not all meetings are closed.')

    @browsing
    def test_deactivating_not_possible_when_unscheduled_proposals_exist(
            self, browser):
        self.login(self.committee_responsible, browser)
        create(
            Builder('proposal').within(self.dossier)
            .having(title=u'Non-scheduled proposal',
                    committee=self.empty_committee.load_model())
            .as_submitted())
        browser.open(self.empty_committee)

        editbar.menu_option('Actions', 'deactivate').click()

        self.assertEqual(Committee.STATE_ACTIVE,
                         self.committee.load_model().get_state())
        statusmessages.assert_message(
            'There are unscheduled proposals submitted to this committee.')

    @browsing
    def test_deactivated_comittee_can_be_reactivated(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.empty_committee)

        editbar.menu_option('Actions', 'deactivate').click()
        editbar.menu_option('Actions', 'reactivate').click()

        self.assertEqual(Committee.STATE_ACTIVE,
                         self.empty_committee.load_model().get_state())
        statusmessages.assert_message('Committee reactivated successfully')

    @browsing
    def test_adding_is_not_available_in_inactive_committee(self, browser):
        self.login(self.committee_responsible, browser)
        browser.open(self.empty_committee)

        self.assertEqual([u'Add new', u'Actions'], editbar.menus())

        editbar.menu_option('Actions', 'deactivate').click()
        self.assertEqual([u'Actions'], editbar.menus())

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
            [
                u'Baubewilligung',
                u'Geb\xfchren',
                u'Freitext Traktandum',
                u'Wiederkehrendes Traktandum',
            ],
            browser.find('Allowed proposal templates').options)
        browser.fill({'Allowed proposal templates': u'Geb\xfchren'}).save()
        self.assertItemsEqual(
            [IUUID(self.proposal_template)],
            self.committee.allowed_proposal_templates)

    @browsing
    def test_visible_fields_in_forms(self, browser):
        """Some fields should only be displayed when the word feature is
        disabled.
        Therefore we test the appearance of all fields.
        """

        fields = ['Title',
                  'Committeeresponsible',
                  'Linked repository folder',
                  'Agendaitem list template',
                  'Table of contents template',
                  'Allowed proposal templates',
                  'Allowed ad-hoc agenda item templates',
                  'Ad hoc agenda item template',
                  'Protocol header template',
                  'Paragraph template',
                  'Agenda item header template for the protocol',
                  'Agenda item suffix template for the protocol',
                  'Protocol suffix template',
                  'Excerpt header template',
                  'Excerpt suffix template']

        with self.login(self.administrator, browser):
            browser.open(self.committee_container)
            factoriesmenu.add('Committee')
            self.assertEquals(
                fields,
                map(methodcaller('normalized_text', recursive=False),
                    browser.css('form#form > fieldset > div.field > label')))

        with self.login(self.committee_responsible, browser):
            browser.open(self.committee, view='edit')
            self.assertEquals(
                fields,
                map(methodcaller('normalized_text', recursive=False),
                    browser.css('form#form > fieldset > div.field > label')))
