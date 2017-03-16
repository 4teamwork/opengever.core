from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import info_messages
from ftw.testbrowser.utils import normalize_spaces
from opengever.core.testing import activate_bumblebee_feature
from opengever.core.testing import OPENGEVER_FUNCTIONAL_DOSSIER_TEMPLATE_LAYER
from opengever.core.testing import toggle_feature
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.dossiertemplate import is_dossier_template_feature_enabled
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateSchema
from opengever.dossier.dossiertemplate.interfaces import IDossierTemplateSettings
from opengever.ogds.base.autocomplete_widget import AutocompleteSelectionWidget
from opengever.ogds.base.interfaces import ISyncStamp
from opengever.testing import FunctionalTestCase
from plone import api
from zExceptions import Unauthorized
from zope.component import getUtility


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
        self.templatefolder = create(Builder('templatefolder'))

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
                                 .within(self.templatefolder))

        browser.login().open(dossiertemplate)

        browser.find('Edit').click()
        browser.fill({'Title': 'Edited Template'}).submit()

        self.assertEquals(['Changes saved'], info_messages())
        self.assertEquals(['Edited Template'], browser.css('h1').text)

    @browsing
    def test_addable_types(self, browser):
        dossiertemplate = create(Builder('dossiertemplate')
                                 .within(self.templatefolder))

        browser.login().open(dossiertemplate)

        self.assertEquals(
            ['Document', 'Subdossier'],
            factoriesmenu.addable_types())

    @browsing
    def test_a_subdossiers_is_a_dossiertemplate(self, browser):
        dossiertemplate = create(Builder('dossiertemplate')
                                 .within(self.templatefolder))

        browser.login().open(dossiertemplate)

        factoriesmenu.add('Subdossier')
        browser.fill({'Title': 'Template'}).submit()

        self.assertTrue(IDossierTemplateSchema.providedBy(browser.context))

    @browsing
    def test_add_form_title_of_dossiertemplate_is_the_default_title(self, browser):
        browser.login().open(self.templatefolder)
        factoriesmenu.add('Dossier template')

        self.assertEqual(
            'Add Dossier template',
            browser.css('#content h1').first.text)

    @browsing
    def test_add_form_title_of_dossiertemplate_as_a_subdossier_contains_subdossier(self, browser):
        dossiertemplate = create(Builder('dossiertemplate')
                                 .within(self.templatefolder))

        browser.login().open(dossiertemplate)
        factoriesmenu.add('Subdossier')

        self.assertEqual(
            'Add Subdossier',
            browser.css('#content h1').first.text)

    @browsing
    def test_edit_form_title_of_dossiertemplate_is_the_default_title(self, browser):
        dossiertemplate = create(Builder('dossiertemplate')
                                 .within(self.templatefolder))

        browser.login().visit(dossiertemplate, view="edit")

        self.assertEqual(
            'Edit Dossier template',
            browser.css('#content h1').first.text)

    @browsing
    def test_edit_form_title_of_dossiertemplate_as_a_subdossier_contains_subdossier(self, browser):
        dossiertemplate = create(Builder('dossiertemplate')
                                 .within(self.templatefolder))

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
                                 .within(self.templatefolder))

        create(Builder('dossiertemplate')
               .titled(u'A Subdossiertemplate')
               .within(dossiertemplate))

        create(Builder('document')
               .titled('Template A')
               .within(self.templatefolder))

        browser.login().visit(self.templatefolder, view="tabbedview_view-dossiertemplates")

        self.assertEqual(
            ['My Dossiertemplate'],
            browser.css('.listing td .linkWrapper').text)

    @browsing
    def test_documents_inside_a_dossiertemplate_will_not_be_listed_in_documents_tab(self, browser):
        create(Builder('document')
               .titled('Good document')
               .within(self.templatefolder))

        dossiertemplate = create(Builder('dossiertemplate')
                                 .titled(u'My Dossiertemplate')
                                 .within(self.templatefolder))

        create(Builder('document')
               .titled('Bad document')
               .within(dossiertemplate))

        browser.login().visit(self.templatefolder, view="tabbedview_view-documents-proxy")

        self.assertEqual(
            ['Good document'],
            browser.css('.listing td .linkWrapper').text)

    @browsing
    def test_show_only_whitelisted_schema_fields_in_add_form(self, browser):
        browser.login().open(self.templatefolder)
        factoriesmenu.add('Dossier template')

        # browser.css('').text will return the text of the current node an all
        # its child-nodes. The help-text is in the same node as the field-title.
        # This means, that we get the title and the helptext if we use .text.
        #
        # The .raw_text will return only the text of the current node but
        # unnormalized. So we have to do it manually.
        # Two empty labels are introduced by the plone default single checkbox
        # widget.
        self.assertEqual([
            u'Title help Recommendation for the title. Will be displayed as a'
            u' help text if you create a dossier from template',
            u'Title',
            u'Description',
            u'Keywords',
            u'The defined keywords will be preselected for new dossies from template.',
            u'Predefined Keywords',
            u'The user can choose only from the defined keywords in a new dossier '
            u'from template. It also prevents the user for creating new keywords',
            u'Restrict Keywords',
            u'Comments',
            u'filing prefix'],
            filter(lambda text: bool(text),
                   browser.css('#content fieldset label').text)
        )

    @browsing
    def test_show_only_whitelisted_schema_fields_in_edit_form(self, browser):
        dossiertemplate = create(Builder('dossiertemplate')
                                 .titled(u'My Dossiertemplate')
                                 .within(self.templatefolder))

        browser.login().visit(dossiertemplate, view="edit")
        self.assertEqual([
            u'Title help Recommendation for the title. Will be displayed as a'
            u' help text if you create a dossier from template',
            u'Title',
            u'Description',
            u'Keywords',
            u'The defined keywords will be preselected for new dossies from template.',
            u'Predefined Keywords',
            u'The user can choose only from the defined keywords in a new dossier '
            u'from template. It also prevents the user for creating new keywords',
            u'Restrict Keywords',
            u'Comments',
            u'filing prefix'],
            filter(lambda text: bool(text),
                   browser.css('#content fieldset label').text)
        )

    @browsing
    def test_dossiertemplate_predefined_keywords_is_there(self, browser):
        dossiertemplate = create(Builder('dossiertemplate')
                                 .titled(u'My Dossiertemplate')
                                 .within(self.templatefolder))

        browser.login().visit(dossiertemplate, view='@@edit')
        self.assertTrue(browser.find_field_by_text('Predefined Keywords'),
                        'Expect the "Predefined Keywords" field')

        form_labels = browser.form_field_labels
        self.assertGreater(form_labels.index('Predefined Keywords'),
                           form_labels.index('Keywords'),
                           '"Predefined Keywords" should be after "Keywords"')

    @browsing
    def test_dossiertemplate_restrict_keywords_is_there(self, browser):
        dossiertemplate = create(Builder('dossiertemplate')
                                 .titled(u'My Dossiertemplate')
                                 .within(self.templatefolder))

        browser.login().visit(dossiertemplate, view='@@edit')
        self.assertTrue(browser.find_field_by_text('Restrict Keywords'),
                        'Expect the "Restrict Keywords" field')

        form_labels = browser.form_field_labels
        self.assertGreater(form_labels.index('Restrict Keywords'),
                           form_labels.index('Predefined Keywords'),
                           '"Restrict Keywords" should be after "Predefined '
                           'Keywords"')


class TestDossierTemplateAddWizard(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_DOSSIER_TEMPLATE_LAYER

    def setUp(self):
        super(TestDossierTemplateAddWizard, self).setUp()
        self.root = create(Builder('repository_root'))
        self.branch_node = create(Builder('repository').within(self.root))
        self.leaf_node = create(Builder('repository').within(self.branch_node))

        self.templatefolder = create(Builder('templatefolder'))

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

    def test_is_not_available_if_user_does_not_have_add_dossier_permission(self):
        self.grant('Reader')

        self.assertFalse(api.user.has_permission(
            'opengever.dossier: Add businesscasedossier', obj=self.leaf_node))

        self.assertFalse(
            self.leaf_node.restrictedTraverse('@@dossier_with_template/is_available')())

    def test_is_available_if_user_has_add_dossier_permission(self):
        self.grant('Reader')

        api.user.grant_roles(
            user=api.user.get_current(),
            obj=self.leaf_node,
            roles=['Contributor'])

        self.assertFalse(api.user.has_permission(
            'opengever.dossier: Add businesscasedossier', obj=self.portal))

        self.assertTrue(api.user.has_permission(
            'opengever.dossier: Add businesscasedossier', obj=self.leaf_node))

        self.assertTrue(
            self.leaf_node.restrictedTraverse('@@dossier_with_template/is_available')())

    def test_raise_not_found_if_access_on_wizard_if_feature_is_not_available(self):
        toggle_feature(IDossierTemplateSettings, enabled=False)

        with self.assertRaises(Unauthorized):
            self.leaf_node.restrictedTraverse('@@dossier_with_template')()

        with self.assertRaises(Unauthorized):
            self.leaf_node.restrictedTraverse('@@add-dossier-from-template')()

    @browsing
    def test_only_show_dossiertemplates_without_subdossiers(self, browser):
        template1 = create(Builder("dossiertemplate")
                           .within(self.templatefolder)
                           .titled(u"Template 1"))

        create(Builder("dossiertemplate")
               .within(template1)
               .titled(u"Subdossier 1"))

        template2 = create(Builder("dossiertemplate")
                           .within(self.templatefolder)
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
    def test_selectable_templates_are_restricted_when_addable_templates_are_selected(self, browser):
        template1 = create(Builder("dossiertemplate")
                           .within(self.templatefolder)
                           .titled(u"Template 1"))
        template2 = create(Builder("dossiertemplate")
                           .within(self.templatefolder)
                           .titled(u"Template 2"))

        leaf_node_2 = create(Builder('repository')
                             .having(addable_dossier_templates=[template2])
                             .within(self.branch_node))

        browser.login().visit(leaf_node_2)
        factoriesmenu.add('Dossier with template')

        self.assertEqual(
            ['Template 2'],
            browser.css('.listing tr td:nth-child(2)').text)

    @browsing
    def test_dossiertemplate_values_are_prefilled_properly_in_the_dossier(self, browser):
        values = {
            'title': u'My template',
            'description': u'Lorem ipsum',
            'keywords': (u'secret', u'special'),
            'comments': 'this is very special',
            'filing_prefix': 'department'
            }

        create(Builder("dossiertemplate").within(self.templatefolder).having(**values))

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
    def test_dossiertemplate_do_not_copy_keywords(self, browser):
        values = {
            'title': u'My template',
            'keywords': (u'special', u'secret'),
            'predefined_keywords': False
            }

        create(Builder("dossiertemplate")
               .within(self.templatefolder)
               .having(**values))

        create(Builder("dossiertemplate")
               .within(self.templatefolder)
               .having(title=u'Another dossiertemplate',
                       keywords=(u'do not appear', u'not there')))

        browser.login().visit(self.leaf_node)
        factoriesmenu.add('Dossier with template')

        token = browser.css(
            'input[name="form.widgets.template"]').first.attrib.get('value')

        browser.fill({'form.widgets.template': token}).submit()
        browser.click_on('Save')

        dossier = browser.context
        self.assertEqual((), IDossier(dossier).keywords)

    @browsing
    def test_dossiertemplate_restrict_keywords(self, browser):
        values = {
            'title': u'My template',
            'keywords': (u'secret\xe4', u'special'),
            'restrict_keywords': True,
            'predefined_keywords': True
            }

        create(Builder("dossiertemplate")
               .within(self.templatefolder)
               .having(**values))

        browser.login().visit(self.leaf_node)
        factoriesmenu.add('Dossier with template')

        token = browser.css(
            'input[name="form.widgets.template"]').first.attrib.get('value')

        browser.fill({'form.widgets.template': token}).submit()
        keywords = browser.find_field_by_text(u'Keywords')

        # The field is there but not visible.
        # It's not really possible to change the behavior of a widget in
        # the update method of a group form. So many update/updateWidget
        # happen in this process.
        # new = browser.css('#' + keywords.attrib['id'] + '_new')
        # self.assertFalse(new, 'It should not be possible to add new terms')

        self.assertItemsEqual(list(values['keywords']),
                              keywords.options_labels)
        browser.click_on('Save')
        self.assertItemsEqual((u'secret\xe4', u'special'),
                              IDossier(browser.context).keywords)

    @browsing
    def test_redirects_to_dossier_after_creating_dossier_from_template(self, browser):
        create(Builder("dossiertemplate")
               .within(self.templatefolder)
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
        template = create(Builder("dossiertemplate")
                          .within(self.templatefolder)
                          .titled(u'Template'))

        template_subdossier_1 = create(Builder("dossiertemplate")
                                       .within(template)
                                       .titled(u'Subdossier 1'))

        create(Builder('document')
               .titled('Document 1')
               .within(template_subdossier_1)
               .with_dummy_content())

        template_subdossier_1_1 = create(Builder("dossiertemplate")
                                         .within(template_subdossier_1)
                                         .titled(u'Subdossier 1.1'))

        create(Builder('document')
               .titled('Document 1.1')
               .within(template_subdossier_1_1)
               .with_dummy_content())

        browser.login().visit(self.leaf_node)
        factoriesmenu.add('Dossier with template')
        token = browser.css(
            'input[name="form.widgets.template"]').first.attrib.get('value')
        browser.fill({'form.widgets.template': token}).submit()
        browser.click_on('Save')

        dossier = browser.context

        self.assertEqual('Template', dossier.title)
        self.assertEqual(
            [u'Subdossier 1'],
            [obj.title for obj in dossier.listFolderContents()],
            "The content of the root-dossier is not correct."
            )

        subdossier_1 = dossier.listFolderContents()[0]
        self.assertEqual(
            [u'Document 1', u'Subdossier 1.1'],
            [obj.title for obj in subdossier_1.listFolderContents()],
            "The content of the subdossier 1 is not correct"
            )

        subdossier_1_1 = subdossier_1.listFolderContents()[1]
        self.assertEqual(
            [u'Document 1.1'],
            [obj.title for obj in subdossier_1_1.listFolderContents()],
            "The content of the subdossier 1.1 is not correct"
            )

    @browsing
    def test_subdossier_has_same_responsible_as_dossier(self, browser):
        create(Builder('ogds_user')
               .id('peter.meier')
               .having(firstname='Peter', lastname='Meier')
               .assign_to_org_units([self.org_unit]))

        # Reset the cachekey for the users-vocabulary.
        # This is necessary, otherwise the user wont be listed
        # in the responsible-autocomplete-widget.
        getUtility(ISyncStamp).set_sync_stamp(
            datetime.now().isoformat(), context=self.portal)

        template = create(Builder("dossiertemplate")
                          .within(self.templatefolder)
                          .titled(u'Template'))

        template_subdossier = create(Builder("dossiertemplate")
                                     .within(template)
                                     .titled(u'Subdossier'))

        self.leaf_node.restrictedTraverse(
            'add-dossier-from-template').form.recursive_content_creation
        browser.login().visit(self.leaf_node)
        factoriesmenu.add('Dossier with template')
        token = browser.css(
            'input[name="form.widgets.template"]').first.attrib.get('value')
        browser.fill({'form.widgets.template': token}).submit()
        browser.fill({'Responsible': 'peter.meier'})
        browser.click_on('Save')

        subdossier = browser.context.listFolderContents()[0]

        self.assertEqual('peter.meier', IDossier(subdossier).responsible)

    @browsing
    def test_prefill_title_if_no_title_help_is_available(self, browser):
        create(Builder("dossiertemplate")
               .within(self.templatefolder)
               .titled(u"My Template"))

        browser.login().visit(self.leaf_node)
        factoriesmenu.add('Dossier with template')

        token = browser.css(
            'input[name="form.widgets.template"]').first.attrib.get('value')

        browser.fill({'form.widgets.template': token}).submit()

        self.assertEqual(
            "My Template",
            browser.css('#formfield-form-widgets-IOpenGeverBase-title input').first.value)

        self.assertEqual(
            [], browser.css('#formfield-form-widgets-IOpenGeverBase-title .formHelp'))

    @browsing
    def test_do_not_fill_title_and_add_title_help_as_description_if_title_help_is_available(self, browser):
        create(Builder("dossiertemplate")
               .within(self.templatefolder)
               .titled(u"My Template")
               .having(title_help=u"This is a helpt text"))

        browser.login().visit(self.leaf_node)
        factoriesmenu.add('Dossier with template')

        token = browser.css(
            'input[name="form.widgets.template"]').first.attrib.get('value')

        browser.fill({'form.widgets.template': token}).submit()

        self.assertEqual(
            "",
            browser.css('#formfield-form-widgets-IOpenGeverBase-title input').first.value)

        self.assertEqual(
            "This is a helpt text",
            browser.css('#formfield-form-widgets-IOpenGeverBase-title .formHelp').first.text)


OVERVIEW_TAB = 'tabbedview_view-overview'
SUBDOSSIERS_TAB = 'tabbedview_view-subdossiers'
DOCUMENTS_LIST_TAB = 'tabbedview_view-documents'
DOCUMENTS_GALLERY_TAB = 'tabbedview_view-documents-gallery'


class TestDossierTemplateOverview(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_DOSSIER_TEMPLATE_LAYER

    def setUp(self):
        super(TestDossierTemplateOverview, self).setUp()
        self.dossiertemplate = create(Builder('dossiertemplate')
                                      .titled(u'My Dossiertemplate')
                                      .having(description=u'This is a description',
                                              keywords=(u'chuck', u'james'),
                                              comments=u'This is a comment',
                                              filing_prefix='directorate'))

    @browsing
    def test_description_box_shows_description(self, browser):
        browser.login().open(self.dossiertemplate, view=OVERVIEW_TAB)
        self.assertEqual(u'This is a description',
                         browser.css('#descriptionBox span').first.text)

    @browsing
    def test_keywords_box_shows_keywords_joined_by_comma(self, browser):
        browser.login().open(self.dossiertemplate, view=OVERVIEW_TAB)
        self.assertEqual(u'chuck, james',
                         browser.css('#keywordsBox span').first.text)

    @browsing
    def test_comments_box_shows_comment(self, browser):
        browser.login().open(self.dossiertemplate, view=OVERVIEW_TAB)
        self.assertEqual(u'This is a comment',
                         browser.css('#commentsBox span').first.text)

    @browsing
    def test_filing_prefix_box_shows_filing_prefix_title(self, browser):
        browser.login().open(self.dossiertemplate, view=OVERVIEW_TAB)
        self.assertEqual(u'Directorate',
                         browser.css('#filing_prefixBox span').first.text)

    @browsing
    def test_document_box_items_are_limited_to_ten_and_sorted_by_sortable_title(self, browser):
        for i in range(1, 11):
            create(Builder('document')
                   .within(self.dossiertemplate)
                   .titled(u'C Document %s' % i))

        create(Builder('document')
               .within(self.dossiertemplate)
               .titled(u'A Document'))
        create(Builder('document')
               .within(self.dossiertemplate)
               .titled(u'B Document'))

        browser.login().open(self.dossiertemplate, view=OVERVIEW_TAB)

        self.assertSequenceEqual(
            ['A Document', 'B Document', 'C Document 1', 'C Document 2', 'C Document 3',
             'C Document 4', 'C Document 5', 'C Document 6', 'C Document 7',
             'C Document 8'],
            browser.css('#documentsBox li:not(.moreLink) a.document_link').text)

    @browsing
    def test_documents_in_overview_are_linked(self, browser):
        document = create(Builder('document')
                          .within(self.dossiertemplate)
                          .titled(u'Document 1'))

        browser.login().open(self.dossiertemplate, view=OVERVIEW_TAB)

        items = browser.css('#documentsBox li:not(.moreLink) a.document_link')

        self.assertEqual(1, len(items))
        self.assertEqual(document.absolute_url(), items.first.get('href'))


class TestDossierTemplateSubdossiers(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_DOSSIER_TEMPLATE_LAYER

    def setUp(self):
        super(TestDossierTemplateSubdossiers, self).setUp()
        self.dossiertemplate = create(Builder('dossiertemplate')
                                      .titled(u'My Dossiertemplate'))

    @browsing
    def test_list_subdossiers_alphabetically(self, browser):
        create(Builder('dossiertemplate')
               .within(self.dossiertemplate)
               .titled(u'A Subdossier'))

        create(Builder('dossiertemplate')
               .within(self.dossiertemplate)
               .titled(u'C Subdossier'))

        create(Builder('dossiertemplate')
               .within(self.dossiertemplate)
               .titled(u'B Subdossier'))

        browser.login().open(self.dossiertemplate, view=SUBDOSSIERS_TAB)

        self.assertEqual(
            ['A Subdossier', 'B Subdossier', 'C Subdossier'],
            browser.css('table.listing a.contenttype-opengever-dossier-dossiertemplate').text)

    @browsing
    def test_list_subdossiers_in_subdossiers(self, browser):
        subdossier_1 = create(Builder('dossiertemplate')
                              .within(self.dossiertemplate)
                              .titled(u'B Subdossier'))

        create(Builder('dossiertemplate')
               .within(subdossier_1)
               .titled(u'A Subdossier'))

        browser.login().open(self.dossiertemplate, view=SUBDOSSIERS_TAB)

        self.assertEqual(
            ['A Subdossier', 'B Subdossier'],
            browser.css('table.listing a.contenttype-opengever-dossier-dossiertemplate').text)


class TestDossierTemplateDocuments(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_DOSSIER_TEMPLATE_LAYER

    def setUp(self):
        super(TestDossierTemplateDocuments, self).setUp()
        self.dossiertemplate = create(Builder('dossiertemplate')
                                      .titled(u'My Dossiertemplate'))

        subdossier = create(Builder('dossiertemplate')
                            .within(self.dossiertemplate))

        create(Builder('document')
               .within(self.dossiertemplate)
               .titled('Document 1'))
        create(Builder('document')
               .within(self.dossiertemplate)
               .titled('Document 3'))
        create(Builder('document')
               .within(subdossier)
               .titled('Document 2'))

    @browsing
    def test_show_documents_in_list_view_sorted_alphabetically(self, browser):
        browser.login().open(self.dossiertemplate, view=DOCUMENTS_LIST_TAB)

        self.assertEqual(
            ['Document 1', 'Document 2', 'Document 3'],
            browser.css('table.listing a.contenttype-opengever-document-document').text)

    @browsing
    def test_show_documents_in_gallery_view_sorted_alphabetically(self, browser):
        activate_bumblebee_feature()
        browser.login().open(self.dossiertemplate, view=DOCUMENTS_GALLERY_TAB)

        self.assertEqual(
            ['Document 1', 'Document 2', 'Document 3'],
            [preview.attrib.get('alt') for preview in browser.css(
                '.preview-listing .file-preview')])
