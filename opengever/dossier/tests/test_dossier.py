from ftw.builder import Builder
from ftw.builder import create
from ftw.contentmenu.menu import FactoriesMenu
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.mail.behaviors import ISendableDocsContainer
from opengever.testing import FunctionalTestCase
from opengever.testing import index_data_for
from Products.CMFCore.utils import getToolByName


class TestDossier(FunctionalTestCase):

    builder_id = 'dossier'
    portal_type = 'opengever.dossier.businesscasedossier'

    def setUp(self):
        super(TestDossier, self).setUp()
        self.dossier = self.create_test_dossier()

    def create_test_dossier(self):
        return create(Builder(self.builder_id))

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

    def _get_active_tabbedview_tab_titles(self, obj):
        types_tool = getToolByName(self.portal, 'portal_types')
        actions = types_tool.listActionInfos(
            object=obj, category='tabbedview-tabs')
        tabs = [action['title'] for action in actions]
        return tabs

    def assert_tabbedview_tabs_for_obj(self, expected_tabs, obj):
        self.assertEquals(expected_tabs,
                          self._get_active_tabbedview_tab_titles(obj))

    def assert_searchable_text(self, expected, dossier):
        values = index_data_for(dossier).get('SearchableText')
        values.sort()

        self.assertEquals(expected, values)

    def test_is_marked_as_sendable_docs_container(self):
        self.assertTrue(
            ISendableDocsContainer.providedBy(self.dossier),
            'The dossier is not marked with the ISendableDocsContainer')

    def test_tabbedview_tabs(self):
        expected_tabs = ['Overview', 'Subdossiers', 'Documents', 'Tasks',
                         'Participants', 'Trash', 'Journal', 'Sharing', ]

        self.assert_tabbedview_tabs_for_obj(expected_tabs, self.dossier)

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
             u'Add Participant'],
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

    def get_factory_menu_items(self, obj):
        menu = FactoriesMenu(obj)
        return menu.getMenuItems(self.dossier, self.dossier.REQUEST)

    def test_default_addable_types(self):
        self.grant('Contributor')
        self.assertItemsEqual(
            ['opengever.document.document', 'ftw.mail.mail',
             'opengever.dossier.businesscasedossier', 'opengever.task.task'],
            [fti.id for fti in self.dossier.allowedContentTypes()])


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
