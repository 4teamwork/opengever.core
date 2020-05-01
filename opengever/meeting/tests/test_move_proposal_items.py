from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import assert_message
from opengever.testing import SolrIntegrationTestCase
from plone import api
from Products.CMFPlone.utils import safe_unicode


class TestMoveProposalItems(SolrIntegrationTestCase):

    @browsing
    def test_move_proposal_to_new_dossier(self, browser):
        self.login(self.regular_user, browser)
        proposal = self.proposal

        payload = {'paths:list': ['/'.join(proposal.getPhysicalPath())]}

        self.assertNotIn(proposal, self.subdossier.objectValues())

        browser.open(self.dossier, payload, view='move_proposal_items')
        browser.fill({'Destination': self.subdossier})
        browser.css('#form-buttons-button_submit').first.click()

        assert_message('1 Elements were moved successfully')
        self.assertIn(proposal, self.subdossier.objectValues())

    @browsing
    def test_redirects_to_context_and_shows_statusmessage_when_obj_cant_be_found(self, browser):
        self.login(self.regular_user, browser)
        payload = {'paths:list': ['/invalid/path']}

        browser.open(self.dossier, payload, view='move_proposal_items')

        browser.fill({'Destination': self.subdossier})
        browser.css('#form-buttons-button_submit').first.click()

        assert_message("The selected objects can't be found, please try it again.")

    @browsing
    def test_proposal_inside_closed_dossier_is_not_movable(self, browser):
        self.login(self.dossier_manager, browser)

        with self.login(self.manager):
            api.content.transition(obj=self.subdossier,
                                   transition="dossier-transition-resolve")

        browser.open(self.subdossier, {}, view='move_proposal_items')

        assert_message('Can only move objects from open dossiers')
        self.assertIn(self.proposal, self.dossier.objectValues())

    @browsing
    def test_do_not_allow_to_move_proposal_into_a_resolved_dossier(self, browser):
        self.login(self.regular_user, browser)

        payload = {'paths:list': ['/'.join(self.proposal.getPhysicalPath())]}

        with self.login(self.manager):
            api.content.transition(obj=self.subdossier,
                                   transition="dossier-transition-resolve")

        browser.open(self.dossier, payload, view='move_proposal_items')
        browser.fill({'Destination': self.subdossier})
        browser.css('#form-buttons-button_submit').first.click()

        self.assertEquals(['Required input is missing.'],
                          browser.css('.fieldErrorBox .error').text,
                          "It's not allowed to select a closed dossier")

    @browsing
    def test_do_not_allow_to_move_proposal_outside_of_main_dossier(self, browser):
        self.login(self.regular_user, browser)

        payload = {'paths:list': ['/'.join(self.proposal.getPhysicalPath())]}

        browser.open(self.dossier, payload, view='move_proposal_items')
        browser.fill({'Destination': self.resolvable_dossier})
        browser.css('#form-buttons-button_submit').first.click()

        self.assertEquals(['Required input is missing.'],
                          browser.css('.fieldErrorBox .error').text,
                          "It's not allowed to select a dossier outside of the "
                          "current main dossier")

    @browsing
    def test_move_target_autocomplete_widget_lists_only_dossiers_of_the_proposals_current_main_dossier(self, browser):
        self.login(self.dossier_responsible, browser)
        autocomplete_url = u'/'.join((
            self.dossier.absolute_url(),
            u'@@move_proposal_items',
            u'++widget++form.widgets.destination_folder',
            u'@@autocomplete-search',
        ))

        sister_dossier = create(Builder('dossier')
                                .titled(safe_unicode(self.dossier.title_or_id()))
                                .within(self.leaf_repofolder))

        # This subdossier in sister_dossier is not found in the autocomplete
        create(Builder('dossier')
               .titled(safe_unicode(self.subsubdossier.title_or_id()))
               .within(sister_dossier))
        self.commit_solr()

        browser.open(u'?'.join((autocomplete_url, u'q={}'.format(self.subsubdossier.title_or_id()))))
        self.assertEqual(
            '/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/dossier-2/dossier-4|Subsubdossier',
            browser.contents,
            'Only the dossier in the main dossier should be found.')

        browser.open(u'?'.join((autocomplete_url, u'q={}'.format(self.dossier.title_or_id()))))
        self.assertEqual(
            '/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1|Vertr\xc3\xa4ge mit der kantonalen Finanzverwaltung',
            browser.contents)

    @browsing
    def test_move_target_autocomplete_widget_does_not_list_closed_dossiers(self, browser):
        self.login(self.dossier_responsible, browser)
        autocomplete_url = u'/'.join((
            self.dossier.absolute_url(),
            u'@@move_proposal_items',
            u'++widget++form.widgets.destination_folder',
            u'@@autocomplete-search',
        ))

        with self.login(self.manager):
            api.content.transition(obj=self.subsubdossier,
                                   transition="dossier-transition-resolve")
        self.commit_solr()

        browser.open(u'?'.join((autocomplete_url, u'q={}'.format(self.subsubdossier.title_or_id()))))
        self.assertEqual('', browser.contents)
