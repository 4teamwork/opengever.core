from ftw.builder import Builder
from ftw.builder import create
from ftw.contentmenu.menu import FactoriesMenu
from ftw.testbrowser import browsing
from opengever.dossier.behaviors.dossier import IDossier
from opengever.mail.behaviors import ISendableDocsContainer
from opengever.testing import IntegrationTestCase
from opengever.testing import SolrIntegrationTestCase
from Products.CMFCore.utils import getToolByName
from zExceptions import Unauthorized


class TestDossier(IntegrationTestCase):

    portal_type = 'opengever.dossier.businesscasedossier'

    def test_get_main_dossier_returns_self_when_is_already_root(self):
        self.login(self.dossier_responsible)

        self.assertEqual(self.dossier,
                         self.dossier.get_main_dossier())

    def test_get_main_dossier_returns_main_for_nested_dossiers(self):
        self.login(self.dossier_responsible)

        sub2 = create(Builder('dossier').within(self.subdossier))

        self.assertEqual(self.dossier,
                         self.subdossier.get_main_dossier())
        self.assertEqual(self.dossier,
                         sub2.get_main_dossier())

    def test_falsy_has_subdossiers(self):
        self.login(self.dossier_responsible)

        self.assertFalse(self.expired_dossier.has_subdossiers())

    def test_truthy_has_subdossiers(self):
        self.login(self.dossier_responsible)

        self.assertTrue(self.dossier.has_subdossiers())

    def test_truthy_has_subdossiers_closed_dossiers(self):
        self.login(self.dossier_responsible)

        create(Builder('dossier')
               .within(self.dossier)
               .in_state('dossier-state-resolved'))
        self.assertTrue(self.dossier.has_subdossiers())

    def test_is_marked_as_sendable_docs_container(self):
        self.login(self.dossier_responsible)

        self.assertTrue(
            ISendableDocsContainer.providedBy(self.dossier),
            'The dossier is not marked with the ISendableDocsContainer')

    @browsing
    def test_tabbedview_tabs(self, browser):
        self.login(self.dossier_responsible, browser)

        expected_tabs = ['Overview', 'Subdossiers', 'Documents', 'Tasks',
                         'Participants', 'Trash', 'Journal', 'Info']

        browser.open(self.dossier, view='tabbed_view')
        self.assertEquals(expected_tabs, browser.css('li.formTab').text)

    def test_use_the_dossier_workflow(self):
        self.login(self.dossier_responsible)

        wf_tool = getToolByName(self.portal, 'portal_workflow')
        self.assertEquals('opengever_dossier_workflow',
                          wf_tool.getWorkflowsFor(self.dossier)[0].id)

    def test_mail_is_not_listed_in_factory_menu(self):
        self.login(self.dossier_responsible)

        menu = FactoriesMenu(self.dossier)
        menu_items = menu.getMenuItems(
            self.dossier, self.dossier.REQUEST)

        self.assertNotIn('ftw.mail.mail',
                         [item.get('id') for item in menu_items])

    def test_factory_menu_sorting(self):
        self.login(self.dossier_responsible)

        menu = FactoriesMenu(self.dossier)
        menu_items = menu.getMenuItems(
            self.dossier, self.dossier.REQUEST)

        self.assertEquals(
            [u'Document',
             'document_with_template',
             u'Task',
             'Add task from template',
             u'Subdossier',
             u'Participant'],
            [item.get('title') for item in menu_items])

    def test_subdossier_add_form_is_called_add_subdossier(self):
        self.login(self.dossier_responsible)

        add_form = self.dossier.unrestrictedTraverse(
            '++add++opengever.dossier.businesscasedossier')

        self.assertEquals('Add Subdossier', add_form.label())

    @browsing
    def test_subdossier_edit_form_is_called_edit_subdossier(self, browser):
        self.login(self.dossier_responsible, browser)

        browser.open(self.subdossier, view='edit')

        self.assertEqual('Edit Subdossier', browser.css('h1').first.text)

    def test_nested_subdossiers_is_not_possible_by_default(self):
        self.login(self.dossier_responsible)

        sub = create(Builder('dossier').within(self.dossier))

        self.assertNotIn('opengever.dossier.businesscasedossier',
                         [fti.id for fti in sub.allowedContentTypes()])

    @browsing
    def test_visiting_dossier_add_form_on_branch_node_raise_unauthorized(self, browser):
        self.login(self.dossier_responsible, browser)

        # XXX This causes an infinite redirection loop between ++add++ and
        # reqiure_login. By enabling exception_bubbling we can catch the
        # Unauthorized exception and end the infinite loop.
        browser.exception_bubbling = True
        with self.assertRaises(Unauthorized):
            # with browser.expect_unauthorized():
            browser.open(
                self.repository_root,
                view='++add++opengever.dossier.businesscasedossier')

    def get_factory_menu_items(self, obj):
        menu = FactoriesMenu(obj)
        return menu.getMenuItems(self.dossier,
                                 self.dossier.REQUEST)

    def test_default_addable_types(self):
        self.login(self.dossier_responsible)
        self.assertItemsEqual(
            ['opengever.document.document',
             'ftw.mail.mail',
             'opengever.dossier.businesscasedossier',
             'opengever.task.task'],
            [fti.id for fti in self.dossier.allowedContentTypes()])

    @browsing
    def test_regular_user_can_add_new_keywords_in_dossier(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.visit(self.dossier, view='@@edit')

        keywords = browser.find_field_by_text(u'Keywords')
        new = browser.css('#' + keywords.attrib['id'] + '_new').first
        new.text = u'New Item\nN\xf6i 3'
        browser.find_button_by_label('Save').click()

        self.assertItemsEqual(('Finanzverwaltung', 'New Item',
                               u'N\xf6i 3', u'Vertr\xe4ge'),
                              IDossier(self.dossier).keywords)

        browser.visit(self.dossier, view='edit')
        keywords = browser.find_field_by_text(u'Keywords')
        self.assertItemsEqual(('Finanzverwaltung', 'New Item',
                               'N=C3=B6i 3', 'Vertr=C3=A4ge'),
                              tuple(keywords.value))


class TestDossierSolr(SolrIntegrationTestCase):

    @browsing
    def test_keywords_are_linked_to_search_on_overview(self, browser):
        self.login(self.dossier_responsible, browser)

        browser.visit(self.dossier, view='@@tabbedview_view-overview')
        browser.find_link_by_text(u'Finanzverwaltung').click()
        search_result = browser.css('.searchResults dt a')

        self.assertEqual(2, len(search_result))
        expected_results = ['Sitzungsdossier 9/2017', u'Vertr\xe4ge mit der kantonalen Finanzverwaltung']
        self.assertItemsEqual(expected_results, search_result.text)

        browser.visit(self.dossier, view='@@tabbedview_view-overview')
        browser.find_link_by_text(u'Vertr\xe4ge', within=browser.css("#keywordsBox")).click()
        search_result = browser.css('.searchResults dt a')

        self.assertEqual(4, len(search_result))
        expected_results = [
            u'Abgeschlossene Vertr\xe4ge',
            u'Inaktive Vertr\xe4ge',
            'Sitzungsdossier 9/2017',
            u'Vertr\xe4ge mit der kantonalen Finanzverwaltung',
        ]
        self.assertItemsEqual(expected_results, search_result.text)


class TestMeetingFeatureTypes(IntegrationTestCase):

    def test_meeting_feature_enabled_addable_types(self):
        self.activate_feature("meeting")
        self.login(self.regular_user)
        self.assertItemsEqual(
            ['opengever.document.document', 'ftw.mail.mail',
             'opengever.dossier.businesscasedossier', 'opengever.task.task',
             'opengever.meeting.proposal'],
            [fti.id for fti in self.meeting_dossier.allowedContentTypes()])
