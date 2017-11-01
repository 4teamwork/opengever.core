from ftw.builder import Builder
from ftw.builder import create
from ftw.contentmenu.menu import FactoriesMenu
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.mail.behaviors import ISendableDocsContainer
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from Products.CMFCore.utils import getToolByName
from zExceptions import Unauthorized


class TestDossier(IntegrationTestCase):

    builder_id = 'dossier'
    portal_type = 'opengever.dossier.businesscasedossier'

    @property
    def dossier_to_test(self):
        return self.dossier

    def test_get_main_dossier_returns_self_when_is_already_root(self):
        self.login(self.dossier_responsible)

        self.assertEqual(self.dossier_to_test,
                         self.dossier_to_test.get_main_dossier())

    def test_get_main_dossier_returns_main_for_nested_dossiers(self):
        self.login(self.dossier_responsible)

        sub1 = create(Builder(self.builder_id).within(self.dossier_to_test))
        sub2 = create(Builder(self.builder_id).within(sub1))

        self.assertEqual(self.dossier_to_test,
                         sub1.get_main_dossier())
        self.assertEqual(self.dossier_to_test,
                         sub2.get_main_dossier())

    def test_falsy_has_subdossiers(self):
        self.login(self.dossier_responsible)

        self.assertFalse(self.archive_dossier.has_subdossiers())

    def test_truthy_has_subdossiers(self):
        self.login(self.dossier_responsible)

        self.assertTrue(self.dossier.has_subdossiers())

    def test_truthy_has_subdossiers_closed_dossiers(self):
        self.login(self.dossier_responsible)

        create(Builder(self.builder_id)
               .within(self.dossier_to_test)
               .in_state('dossier-state-resolved'))
        self.assertTrue(self.dossier_to_test.has_subdossiers())

    def test_is_marked_as_sendable_docs_container(self):
        self.login(self.dossier_responsible)

        self.assertTrue(
            ISendableDocsContainer.providedBy(self.dossier_to_test),
            'The dossier is not marked with the ISendableDocsContainer')

    @browsing
    def test_tabbedview_tabs(self, browser):
        self.login(self.dossier_responsible, browser)

        expected_tabs = ['Overview', 'Subdossiers', 'Documents', 'Tasks',
                         'Participants', 'Trash', 'Journal', 'Info']

        browser.open(self.dossier_to_test, view='tabbed_view')
        self.assertEquals(expected_tabs, browser.css('li.formTab').text)

    def test_use_the_dossier_workflow(self):
        self.login(self.dossier_responsible)

        wf_tool = getToolByName(self.portal, 'portal_workflow')
        self.assertEquals('opengever_dossier_workflow',
                          wf_tool.getWorkflowsFor(self.dossier_to_test)[0].id)

    def test_mail_is_not_listed_in_factory_menu(self):
        self.login(self.dossier_responsible)

        menu = FactoriesMenu(self.dossier_to_test)
        menu_items = menu.getMenuItems(
            self.dossier_to_test, self.dossier_to_test.REQUEST)

        self.assertNotIn('ftw.mail.mail',
                         [item.get('id') for item in menu_items])

    def test_factory_menu_sorting(self):
        self.login(self.dossier_responsible)

        menu = FactoriesMenu(self.dossier_to_test)
        menu_items = menu.getMenuItems(
            self.dossier_to_test, self.dossier_to_test.REQUEST)

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

        add_form = self.dossier_to_test.unrestrictedTraverse(
            '++add++{}'.format(self.portal_type))

        self.assertEquals('Add Subdossier', add_form.label())

    def test_subdossier_edit_form_is_called_edit_subdossier(self):
        self.login(self.dossier_responsible)

        sub = create(Builder(self.builder_id).within(self.dossier_to_test))
        edit_form = sub.unrestrictedTraverse('@@edit')
        self.assertEquals('Edit Subdossier', edit_form.label)

    def test_nested_subdossiers_is_not_possible_by_default(self):
        self.login(self.dossier_responsible)

        sub = create(Builder('dossier').within(self.dossier_to_test))

        self.assertNotIn(self.portal_type,
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
                view='++add++{}'.format(self.portal_type))

    def get_factory_menu_items(self, obj):
        menu = FactoriesMenu(obj)
        return menu.getMenuItems(self.dossier_to_test,
                                 self.dossier_to_test.REQUEST)

    def test_default_addable_types(self):
        self.login(self.dossier_responsible)
        self.assertItemsEqual(
            ['opengever.document.document', 'ftw.mail.mail',
             'opengever.dossier.businesscasedossier', 'opengever.task.task'],
            [fti.id for fti in self.dossier_to_test.allowedContentTypes()])

    @browsing
    def test_regular_user_can_add_new_keywords_in_dossier(self, browser):
        self.login(self.dossier_responsible, browser)
        browser.visit(self.dossier_to_test, view='@@edit')

        keywords = browser.find_field_by_text(u'Keywords')
        new = browser.css('#' + keywords.attrib['id'] + '_new').first
        new.text = u'New Item\nN\xf6i 3'
        browser.find_button_by_label('Save').click()

        browser.visit(self.dossier_to_test, view='edit')
        keywords = browser.find_field_by_text(u'Keywords')
        self.assertTupleEqual(('Finanzverwaltung', 'New Item',
                               'N=C3=B6i 3', 'Vertr=C3=A4ge'),
                              tuple(keywords.value))

    @browsing
    def test_keywords_are_linked_to_search_on_overview(self, browser):
        self.login(self.dossier_responsible, browser)

        browser.visit(self.dossier_to_test, view='@@tabbedview_view-overview')
        browser.find_link_by_text(u'Finanzverwaltung').click()
        search_result = browser.css('.searchResults dt a')

        self.assertEquals(2, len(search_result))
        self.assertEquals(self.dossier.title, search_result.first.text)
        self.assertIn(self.meeting_dossier.title, search_result.text)

        browser.visit(self.dossier_to_test, view='@@tabbedview_view-overview')
        browser.find_link_by_text(u'Vertr\xe4ge').click()
        search_result = browser.css('.searchResults dt a')

        self.assertEquals(3, len(search_result))
        self.assertIn(self.dossier.title, search_result.text)
        self.assertIn(self.meeting_dossier.title, search_result.text)
        self.assertIn(self.archive_dossier.title, search_result.text)


class TestMeetingFeatureTypes(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestMeetingFeatureTypes, self).setUp()
        self.dossier_to_test = create(Builder('dossier'))

    def test_meeting_feature_enabled_addable_types(self):
        self.grant('Contributor')
        self.assertItemsEqual(
            ['opengever.document.document', 'ftw.mail.mail',
             'opengever.dossier.businesscasedossier', 'opengever.task.task',
             'opengever.meeting.proposal'],
            [fti.id for fti in self.dossier_to_test.allowedContentTypes()])
