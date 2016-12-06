from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.base.default_values import get_persisted_values_for_obj
from opengever.core.testing import OPENGEVER_FUNCTIONAL_DOSSIER_TEMPLATE_LAYER
from opengever.core.testing import toggle_feature
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.dossiertemplate import is_dossier_template_feature_enabled
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateSchema
from opengever.dossier.dossiertemplate.interfaces import IDossierTemplateSettings
from opengever.ogds.base.autocomplete_widget import AutocompleteSelectionWidget
from opengever.testing import FunctionalTestCase
from plone import api


class TestIsDossierTemplateFeatureEnabled(FunctionalTestCase):

    def test_true_if_registry_entry_is_true(self):
        api.portal.set_registry_record(
            'is_feature_enabled', True, interface=IDossierTemplateSettings)

        self.assertTrue(is_dossier_template_feature_enabled())

    def test_false_if_registry_entry_is_false(self):
        api.portal.set_registry_record(
            'is_feature_enabled', False, interface=IDossierTemplateSettings)

        self.assertFalse(is_dossier_template_feature_enabled())


class TestDossierTemplate(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_DOSSIER_TEMPLATE_LAYER

    def setUp(self):
        super(TestDossierTemplate, self).setUp()
        self.templatedossier = create(Builder('templatedossier'))

    def test_templatedosisers_does_not_provide_dossier_interface(self):
        dossiertemplate = create(Builder('dossiertemplate'))
        self.assertFalse(IDossierMarker.providedBy(dossiertemplate))

    def test_id_is_sequence_number_prefixed_with_dossiertemplate(self):
        dossiertemplate1 = create(Builder("dossiertemplate"))
        dossiertemplate2 = create(Builder("dossiertemplate"))

        self.assertEquals("dossiertemplate-1", dossiertemplate1.id)
        self.assertEquals("dossiertemplate-2", dossiertemplate2.id)

    def test_dossiertemplate_provides_the_IDossierTemplate_behavior(self):
        dossiertemplate = create(Builder('dossiertemplate'))
        self.assertTrue(IDossierTemplateSchema.providedBy(dossiertemplate))

    @browsing
    def test_adding_dossiertemplate_works_properly(self, browser):
        browser.login().open(self.portal)
        factoriesmenu.add('Dossier template')
        browser.fill({'Title': 'Template'}).submit()

        self.assertEquals(['Item created'], info_messages())
        self.assertEquals(['Template'], browser.css('h1').text)

    @browsing
    def test_edit_dossiertemplate_works_properly(self, browser):
        dossiertemplate = create(Builder('dossiertemplate')
                                 .within(self.templatedossier))

        browser.login().open(dossiertemplate)

        browser.find('Edit').click()
        browser.fill({'Title': 'Edited Template'}).submit()

        self.assertEquals(['Changes saved'], info_messages())
        self.assertEquals(['Edited Template'], browser.css('h1').text)

    @browsing
    def test_addable_types(self, browser):
        dossiertemplate = create(Builder('dossiertemplate')
                                 .within(self.templatedossier))

        browser.login().open(dossiertemplate)

        self.assertEquals(
            ['Document', 'Subdossier'],
            factoriesmenu.addable_types())

    @browsing
    def test_a_subdossiers_is_a_dossiertemplate(self, browser):
        dossiertemplate = create(Builder('dossiertemplate')
                                 .within(self.templatedossier))

        browser.login().open(dossiertemplate)

        factoriesmenu.add('Subdossier')
        browser.fill({'Title': 'Template'}).submit()

        self.assertTrue(IDossierTemplateSchema.providedBy(browser.context))

    @browsing
    def test_add_form_title_of_dossiertemplate_is_the_default_title(self, browser):
        browser.login().open(self.templatedossier)
        factoriesmenu.add('Dossier template')

        self.assertEqual(
            'Add Dossier template',
            browser.css('#content h1').first.text)

    @browsing
    def test_add_form_title_of_dossiertemplate_as_a_subdossier_contains_subdossier(self, browser):
        dossiertemplate = create(Builder('dossiertemplate')
                                 .within(self.templatedossier))

        browser.login().open(dossiertemplate)
        factoriesmenu.add('Subdossier')

        self.assertEqual(
            'Add Subdossier',
            browser.css('#content h1').first.text)

    @browsing
    def test_edit_form_title_of_dossiertemplate_is_the_default_title(self, browser):
        dossiertemplate = create(Builder('dossiertemplate')
                                 .within(self.templatedossier))

        browser.login().visit(dossiertemplate, view="edit")

        self.assertEqual(
            'Edit Dossier template',
            browser.css('#content h1').first.text)

    @browsing
    def test_edit_form_title_of_dossiertemplate_as_a_subdossier_contains_subdossier(self, browser):
        dossiertemplate = create(Builder('dossiertemplate')
                                 .within(self.templatedossier))

        subdossiertemplate = create(Builder('dossiertemplate')
                                    .within(dossiertemplate))

        browser.login().visit(subdossiertemplate, view="edit")

        self.assertEqual(
            'Edit Subdossier',
            browser.css('#content h1').first.text)

    @browsing
    def test_dossiertemplates_tab_lists_only_dossiertemplates_without_subdossiers(self, browser):
        dossiertemplate = create(Builder('dossiertemplate')
                                 .titled(u'My Dossiertemplate')
                                 .within(self.templatedossier))

        create(Builder('dossiertemplate')
               .titled(u'A Subdossiertemplate')
               .within(dossiertemplate))

        create(Builder('document')
               .titled('Template A')
               .within(self.templatedossier))

        browser.login().visit(self.templatedossier, view="tabbedview_view-dossiertemplates")

        self.assertEqual(
            ['My Dossiertemplate'],
            browser.css('.listing td .linkWrapper').text)

    @browsing
    def test_documents_inside_a_dossiertemplate_will_not_be_listed_in_documents_tab(self, browser):
        create(Builder('document')
               .titled('Good document')
               .within(self.templatedossier))

        dossiertemplate = create(Builder('dossiertemplate')
                                 .titled(u'My Dossiertemplate')
                                 .within(self.templatedossier))

        create(Builder('document')
               .titled('Bad document')
               .within(dossiertemplate))

        browser.login().visit(self.templatedossier, view="tabbedview_view-documents-proxy")

        self.assertEqual(
            ['Good document'],
            browser.css('.listing td .linkWrapper').text)

    @browsing
    def test_show_only_whitelisted_schema_fields_in_add_form(self, browser):
        browser.login().open(self.templatedossier)
        factoriesmenu.add('Dossier template')

        self.assertEqual(
            [u'Title', 'Description', 'Keywords', 'Comments', 'filing prefix'],
            browser.css('#content fieldset label').text
        )

    @browsing
    def test_show_only_whitelisted_schema_fields_in_edit_form(self, browser):
        dossiertemplate = create(Builder('dossiertemplate')
                                 .titled(u'My Dossiertemplate')
                                 .within(self.templatedossier))

        browser.login().visit(dossiertemplate, view="edit")

        self.assertEqual(
            [u'Title', 'Description', 'Keywords', 'Comments', 'filing prefix'],
            browser.css('#content fieldset label').text
        )


class TestDossierTemplateAddWizard(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_DOSSIER_TEMPLATE_LAYER

    def setUp(self):
        super(TestDossierTemplateAddWizard, self).setUp()
        self.root = create(Builder('repository_root'))
        self.branch_node = create(Builder('repository').within(self.root))
        self.leaf_node = create(Builder('repository').within(self.branch_node))

        self.templatedossier = create(Builder('templatedossier'))

    def test_is_not_available_if_dossiertempalte_feature_is_disabled(self):
        toggle_feature(IDossierTemplateSettings, enabled=False)

        self.assertFalse(
            self.leaf_node.restrictedTraverse('@@dossier_with_template/is_available')())

    def test_is_not_available_on_branch_node(self):
        self.assertFalse(
            self.branch_node.restrictedTraverse('@@dossier_with_template/is_available')())

    def test_is_available_on_leaf_node_when_feature_is_enabled(self):
        self.assertTrue(
            self.leaf_node.restrictedTraverse('@@dossier_with_template/is_available')())

    @browsing
    def test_only_show_dossiertemplates_without_subdossiers(self, browser):
        template1 = create(Builder("dossiertemplate")
                           .within(self.templatedossier)
                           .titled(u"Template 1"))

        create(Builder("dossiertemplate")
               .within(template1)
               .titled(u"Subdossier 1"))

        template2 = create(Builder("dossiertemplate")
                           .within(self.templatedossier)
                           .titled(u"Template 2"))

        create(Builder("dossiertemplate")
               .within(template2)
               .titled(u"Subdossier 2"))

        browser.login().visit(self.leaf_node)
        factoriesmenu.add('Dossier with template')

        self.assertEqual(
            ['Template 1', 'Template 2'],
            browser.css('.listing tr td:nth-child(2)').text)

    @browsing
    def test_dossiertemplate_values_are_prefilled_properly_in_the_dossier(self, browser):
        values = {
            'title': u'My template',
            'description': u'Lorem ipsum',
            'keywords': (u'special', u'secret'),
            'comments': 'this is very special',
            'filing_prefix': 'department'
            }

        create(Builder("dossiertemplate").within(self.templatedossier).having(**values))

        browser.login().visit(self.leaf_node)
        factoriesmenu.add('Dossier with template')

        token = browser.css(
            'input[name="form.widgets.template"]').first.attrib.get('value')

        browser.fill({'form.widgets.template': token}).submit()

        browser.click_on('Save')

        dossier = browser.context

        self.assertEqual(values.get('title'), dossier.title)
        self.assertEqual(values.get('description'), dossier.description)
        self.assertEqual(values.get('keywords'), IDossier(dossier).keywords)
        self.assertEqual(values.get('comments'), IDossier(dossier).comments)
        self.assertEqual(values.get('filing_prefix'), IDossier(dossier).filing_prefix)

    @browsing
    def test_redirects_to_dossier_after_creating_dossier_from_template(self, browser):
        create(Builder("dossiertemplate")
               .within(self.templatedossier)
               .titled(u"My Template"))

        browser.login().visit(self.leaf_node)
        factoriesmenu.add('Dossier with template')

        token = browser.css(
            'input[name="form.widgets.template"]').first.attrib.get('value')

        browser.fill({'form.widgets.template': token}).submit()

        browser.click_on('Save')

        self.assertEqual(self.leaf_node.listFolderContents()[0], browser.context)

    def test_traversing_to_autocomplete_selection_widget_in_add_dossier_template_view_is_possible(self):
        autocomplete_selection_widget = self.leaf_node.unrestrictedTraverse(
            'add-dossier-from-template/++widget++IDossier.responsible')

        self.assertIsInstance(
            autocomplete_selection_widget,
            AutocompleteSelectionWidget)

    @browsing
    def test_redirects_to_first_step_if_the_user_skips_the_first_wizard_step(self, browser):
        browser.login().visit(self.leaf_node, view="add-dossier-from-template")

        self.assertEqual(
            '{}/dossier_with_template'.format(self.leaf_node.absolute_url()),
            browser.url)

    @browsing
    def test_add_recursive_documents_and_subdossiers(self, browser):
        templatedossier = create(Builder('templatedossier'))

        root = create(Builder('repository_root'))
        leaf_node = create(Builder('repository').within(root))

        template = create(Builder("dossiertemplate")
                          .within(templatedossier)
                          .titled(u'Template'))

        create(Builder('document')
               .titled('Document')
               .within(template)
               .with_dummy_content())

        template_subdossier_1 = create(Builder("dossiertemplate")
                                       .within(template)
                                       .titled(u'Subdossier 1'))

        create(Builder('document')
               .titled('Document 1')
               .within(template_subdossier_1)
               .with_dummy_content())

        template_subdossier_2 = create(Builder("dossiertemplate")
                                       .within(template)
                                       .titled(u'Subdossier 2'))

        template_subdossier_2_1 = create(Builder("dossiertemplate")
                                         .within(template_subdossier_2)
                                         .titled(u'Subdossier 2.1'))

        create(Builder('document')
               .titled('Document 2.1')
               .within(template_subdossier_2_1)
               .with_dummy_content())

        browser.login().visit(leaf_node)
        factoriesmenu.add('Dossier with template')

        token = browser.css(
            'input[name="form.widgets.template"]').first.attrib.get('value')

        browser.fill({'form.widgets.template': token}).submit()

        browser.find('Save').click()

        dossier = browser.context

        self.assertEqual('Template', dossier.title)
        self.assertEqual(
            [u'Document', u'Subdossier 1', u'Subdossier 2'],
            [obj.title for obj in dossier.listFolderContents()],
            "The content of the root-dossier is not correct."
            )

        subdossier_1 = dossier.listFolderContents()[1]
        self.assertEqual(
            [u'Document 1'],
            [obj.title for obj in subdossier_1.listFolderContents()],
            "The content of the subdossier 1 is not correct"
            )

        subdossier_2 = dossier.listFolderContents()[2]
        self.assertEqual(
            [u'Subdossier 2.1'],
            [obj.title for obj in subdossier_2.listFolderContents()],
            "The content of the subdossier 2 is not correct"
            )

        subdossier_2_1 = subdossier_2.listFolderContents()[0]
        self.assertEqual(
            [u'Document 2.1'],
            [obj.title for obj in subdossier_2_1.listFolderContents()],
            "The content of the subdossier 2.1 is not correct"
            )
