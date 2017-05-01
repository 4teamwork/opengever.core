from ftw.builder import Builder
from ftw.builder import create
from ftw.contentmenu.menu import FactoriesMenu
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.mail.behaviors import ISendableDocsContainer
from opengever.testing import FunctionalTestCase
from opengever.testing import index_data_for
from plone.app.testing import TEST_USER_ID
from Products.CMFCore.utils import getToolByName
from zExceptions import Unauthorized


class TestDossier(FunctionalTestCase):

    builder_id = 'dossier'
    portal_type = 'opengever.dossier.businesscasedossier'

    def setUp(self):
        super(TestDossier, self).setUp()
        self.dossier = self.create_test_dossier()

    def create_test_dossier(self):
        return create(Builder(self.builder_id)
                      .titled(u'Test Dossier')
                      .having(responsible=TEST_USER_ID))

    def test_get_main_dossier_returns_self_when_is_already_root(self):
        self.assertEqual(self.dossier, self.dossier.get_main_dossier())

    def test_get_main_dossier_returns_main_for_nested_dossiers(self):
        sub1 = create(Builder(self.builder_id).within(self.dossier))
        sub2 = create(Builder(self.builder_id).within(sub1))

        self.assertEqual(self.dossier, sub1.get_main_dossier())
        self.assertEqual(self.dossier, sub2.get_main_dossier())

    def test_falsy_has_subdossiers(self):
        self.assertFalse(self.dossier.has_subdossiers())

    def test_truthy_has_subdossiers(self):
        create(Builder(self.builder_id).within(self.dossier))
        self.assertTrue(self.dossier.has_subdossiers())

    def test_truthy_has_subdossiers_closed_dossiers(self):
        create(Builder(self.builder_id)
               .within(self.dossier)
               .in_state('dossier-state-resolved'))
        self.assertTrue(self.dossier.has_subdossiers())

    def assert_searchable_text(self, expected, dossier):
        values = index_data_for(dossier).get('SearchableText')
        values.sort()

        self.assertEquals(expected, values)

    def test_is_marked_as_sendable_docs_container(self):
        self.assertTrue(
            ISendableDocsContainer.providedBy(self.dossier),
            'The dossier is not marked with the ISendableDocsContainer')

    @browsing
    def test_tabbedview_tabs(self, browser):
        expected_tabs = ['Overview', 'Subdossiers', 'Documents', 'Tasks',
                         'Participants', 'Trash', 'Journal', 'Info']

        browser.login().open(self.dossier, view='tabbed_view')
        self.assertEquals(expected_tabs, browser.css('li.formTab').text)

    def test_use_the_dossier_workflow(self):
        wf_tool = getToolByName(self.portal, 'portal_workflow')
        self.assertEquals('opengever_dossier_workflow',
                          wf_tool.getWorkflowsFor(self.dossier)[0].id)

    def test_mail_is_not_listed_in_factory_menu(self):
        menu = FactoriesMenu(self.dossier)
        menu_items = menu.getMenuItems(self.dossier, self.dossier.REQUEST)

        self.assertNotIn('ftw.mail.mail',
                         [item.get('id') for item in menu_items])

    def test_factory_menu_sorting(self):
        menu = FactoriesMenu(self.dossier)
        menu_items = menu.getMenuItems(self.dossier, self.dossier.REQUEST)

        self.assertEquals(
            [u'Document',
             'document_with_template',
             u'Task',
             'Add task from template',
             u'Subdossier',
             u'Participant'],
            [item.get('title') for item in menu_items])

    def test_subdossier_add_form_is_called_add_subdossier(self):
        add_form = self.dossier.unrestrictedTraverse(
            '++add++{}'.format(self.portal_type))

        self.assertEquals('Add Subdossier', add_form.label())

    def test_subdossier_edit_form_is_called_edit_subdossier(self):
        sub = create(Builder(self.builder_id).within(self.dossier))
        edit_form = sub.unrestrictedTraverse('@@edit')
        self.assertEquals('Edit Subdossier', edit_form.label)

    def test_nested_subdossiers_is_not_possible_by_default(self):
        sub = create(Builder('dossier').within(self.dossier))

        self.assertNotIn(self.portal_type,
                         [fti.id for fti in sub.allowedContentTypes()])

    @browsing
    def test_visiting_dossier_add_form_on_branch_node_raise_unauthorized(self, browser):
        branch_node = create(Builder('repository'))
        create(Builder('repository').within(branch_node))

        # XXX This causes an infinite redirection loop between ++add++ and
        # reqiure_login. By enabling exception_bubbling we can catch the
        # Unauthorized exception and end the infinite loop.
        browser.exception_bubbling = True
        with self.assertRaises(Unauthorized):
        # with browser.expect_unauthorized():
            browser.login().open(
                branch_node, view='++add++{}'.format(self.portal_type))

    def get_factory_menu_items(self, obj):
        menu = FactoriesMenu(obj)
        return menu.getMenuItems(self.dossier, self.dossier.REQUEST)

    def test_default_addable_types(self):
        self.grant('Contributor')
        self.assertItemsEqual(
            ['opengever.document.document', 'ftw.mail.mail',
             'opengever.dossier.businesscasedossier', 'opengever.task.task'],
            [fti.id for fti in self.dossier.allowedContentTypes()])

    @browsing
    def test_regular_user_can_add_new_keywords_in_dossier(self, browser):
        self.grant('Reader', 'Contributor', 'Editor')
        browser.login().visit(self.dossier, view='@@edit')

        keywords = browser.find_field_by_text(u'Keywords')
        new = browser.css('#' + keywords.attrib['id'] + '_new').first
        new.text = u'NewItem1\nNew Item 2\nN\xf6i 3'
        browser.find_button_by_label('Save').click()

        browser.visit(self.dossier, view='edit')
        keywords = browser.find_field_by_text(u'Keywords')
        self.assertTupleEqual(('New Item 2', 'NewItem1', 'N=C3=B6i 3'),
                              tuple(keywords.value))


class TestMeetingFeatureTypes(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestMeetingFeatureTypes, self).setUp()
        self.dossier = create(Builder('dossier'))

    def test_meeting_feature_enabled_addable_types(self):
        self.grant('Contributor')
        self.assertItemsEqual(
            ['opengever.document.document', 'ftw.mail.mail',
             'opengever.dossier.businesscasedossier', 'opengever.task.task',
             'opengever.meeting.proposal'],
            [fti.id for fti in self.dossier.allowedContentTypes()])
