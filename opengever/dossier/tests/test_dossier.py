from ftw.builder import Builder
from ftw.builder import create
from ftw.contentmenu.menu import FactoriesMenu
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

    def assert_additional_attributes_overview_box_labels(self, expected, obj):
        overview = obj.restrictedTraverse('tabbedview_view-overview')
        additional_widgets = overview.additional_attributes()

        self.assertEquals(
            expected, [widget.label for widget in additional_widgets])

    def assert_additional_attributes_overview_box_values(self, expected, obj):
        overview = obj.restrictedTraverse('tabbedview_view-overview')
        additional_widgets = overview.additional_attributes()

        self.assertEquals(
            expected, [widget.value for widget in additional_widgets])

    def assert_tabbedview_tabs_for_obj(self, expected_tabs, obj):
        types_tool = getToolByName(self.portal, 'portal_types')
        actions = types_tool.listActions(object=obj)
        tabs = [action.title for
                action in actions if action.category == 'tabbedview-tabs']

        self.assertEquals(expected_tabs, tabs)

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
                         'Proposals', 'Participants', 'Trash', 'Journal',
                         'Sharing', ]

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
