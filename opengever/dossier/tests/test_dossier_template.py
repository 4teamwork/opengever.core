from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.core.testing import toggle_feature
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.dossiertemplate import is_dossier_template_feature_enabled
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateSchema
from opengever.dossier.dossiertemplate.interfaces import IDossierTemplateSettings
from opengever.dossier.interfaces import IDossierContainerTypes
from opengever.testing import IntegrationTestCase
from plone import api
from zExceptions import Unauthorized


class TestIsDossierTemplateFeatureEnabled(IntegrationTestCase):

    def test_true_if_registry_entry_is_true(self):
        api.portal.set_registry_record(
            'is_feature_enabled', True, interface=IDossierTemplateSettings)

        self.assertTrue(is_dossier_template_feature_enabled())

    def test_false_if_registry_entry_is_false(self):
        api.portal.set_registry_record(
            'is_feature_enabled', False, interface=IDossierTemplateSettings)

        self.assertFalse(is_dossier_template_feature_enabled())


class TestDossierTemplate(IntegrationTestCase):

    features = ('dossiertemplate', )

    def test_templatedossiers_does_not_provide_dossier_interface(self):
        self.login(self.administrator)

        self.assertFalse(IDossierMarker.providedBy(self.dossiertemplate))

    def test_id_is_sequence_number_prefixed_with_dossiertemplate(self):
        self.login(self.administrator)

        self.assertEquals("dossiertemplate-1", self.dossiertemplate.id)

    def test_dossiertemplate_provides_the_IDossierTemplate_behavior(self):
        self.login(self.administrator)

        self.assertTrue(IDossierTemplateSchema.providedBy(self.dossiertemplate))

    @browsing
    def test_adding_dossiertemplate_works_properly(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.templates)
        factoriesmenu.add('Dossier template')
        browser.fill({'Title': 'Template'}).submit()

        self.assertEquals(['Item created'], info_messages())
        self.assertEquals(['Template'], browser.css('h1').text)

    @browsing
    def test_edit_dossiertemplate_works_properly(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.dossiertemplate)
        browser.find('Edit').click()
        browser.fill({'Title': 'Edited Template'}).submit()

        self.assertEquals(['Changes saved'], info_messages())
        self.assertEquals(['Edited Template'], browser.css('h1').text)

    @browsing
    def test_addable_types(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.dossiertemplate)

        self.assertEquals(
            ['Document', 'Subdossier'], factoriesmenu.addable_types())

    @browsing
    def test_a_subdossiers_is_a_dossiertemplate(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.dossiertemplate)

        factoriesmenu.add('Subdossier')
        browser.fill({'Title': 'Template'}).submit()

        self.assertTrue(IDossierTemplateSchema.providedBy(browser.context))

    @browsing
    def test_add_form_title_of_dossiertemplate_is_the_default_title(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.templates)

        factoriesmenu.add('Dossier template')

        self.assertEqual(
            'Add Dossier template',
            browser.css('#content h1').first.text)

    @browsing
    def test_add_form_title_of_dossiertemplate_as_a_subdossier_contains_subdossier(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.dossiertemplate)
        factoriesmenu.add('Subdossier')

        self.assertEqual(
            'Add Subdossier',
            browser.css('#content h1').first.text)

    @browsing
    def test_edit_form_title_of_dossiertemplate_is_the_default_title(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.dossiertemplate, view="edit")

        self.assertEqual(
            'Edit Dossier template',
            browser.css('#content h1').first.text)

    @browsing
    def test_edit_form_title_of_dossiertemplate_as_a_subdossier_contains_subdossier(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.subdossiertemplate, view="edit")

        self.assertEqual(
            'Edit Subdossier',
            browser.css('#content h1').first.text)

    @browsing
    def test_dossiertemplates_tab_lists_only_dossiertemplates_without_subdossiers(self, browser):
        self.login(self.administrator, browser=browser)

        browser.login().visit(self.templates, view="tabbedview_view-dossiertemplates")

        self.assertEqual(
            ['Bauvorhaben klein'],
            browser.css('.listing td .linkWrapper').text)

    @browsing
    def test_documents_inside_a_dossiertemplate_will_not_be_listed_in_documents_tab(self, browser):
        self.login(self.administrator, browser=browser)

        create(Builder('document')
               .titled(u'Dossiertemplate document')
               .within(self.dossiertemplate))

        browser.open(self.templates, view="tabbedview_view-documents-proxy")

        expected_documents = [
            u'T\xc3\xb6mpl\xc3\xb6te Mit',
            u'T\xc3\xb6mpl\xc3\xb6te Ohne',
            u'T\xc3\xb6mpl\xc3\xb6te Normal',
            u'T\xc3\xb6mpl\xc3\xb6te Leer',
            ]

        self.assertEqual(expected_documents, browser.css('.listing td .linkWrapper').text)

    @browsing
    def test_show_only_whitelisted_schema_fields_in_add_form(self, browser):
        self.maxDiff = None
        self.login(self.administrator, browser=browser)
        browser.open(self.templates)
        factoriesmenu.add('Dossier template')

        self.assertEqual([
            u'Title help',
            u'Title',
            u'Description',
            u'Keywords',
            u'Predefined Keywords',
            u'Restrict Keywords',
            u'Comments',
            u'filing prefix'],
            browser.css('#content fieldset label').text
        )

    @browsing
    def test_show_only_whitelisted_schema_fields_in_edit_form(self, browser):
        self.maxDiff = None
        self.login(self.administrator, browser=browser)
        browser.open(self.dossiertemplate, view="edit")
        self.assertEqual([
            u'Title help',
            u'Title',
            u'Description',
            u'Keywords',
            u'Predefined Keywords',
            u'Restrict Keywords',
            u'Comments',
            u'filing prefix'],
            browser.css('#content fieldset label').text
        )

    @browsing
    def test_dossiertemplate_predefined_keywords_is_there(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.dossiertemplate, view="edit")

        self.assertTrue(browser.find_field_by_text('Predefined Keywords'),
                        'Expect the "Predefined Keywords" field')

        form_labels = browser.form_field_labels
        self.assertGreater(form_labels.index('Predefined Keywords'),
                           form_labels.index('Keywords'),
                           '"Predefined Keywords" should be after "Keywords"')

    @browsing
    def test_dossiertemplate_restrict_keywords_is_there(self, browser):
        self.login(self.administrator, browser=browser)
        browser.open(self.dossiertemplate, view="edit")

        self.assertTrue(browser.find_field_by_text('Restrict Keywords'),
                        'Expect the "Restrict Keywords" field')

        form_labels = browser.form_field_labels
        self.assertGreater(form_labels.index('Restrict Keywords'),
                           form_labels.index('Predefined Keywords'),
                           '"Restrict Keywords" should be after "Predefined '
                           'Keywords"')


class TestDossierTemplateAddWizard(IntegrationTestCase):

    features = ('dossiertemplate', )

    def test_is_not_available_if_dossiertempalte_feature_is_disabled(self):
        self.login(self.regular_user)

        toggle_feature(IDossierTemplateSettings, enabled=False)

        self.assertFalse(
            self.leaf_repofolder.restrictedTraverse(
                '@@dossier_with_template/is_available')())

    def test_is_not_available_on_branch_node(self):
        self.login(self.regular_user)

        self.assertFalse(
            self.branch_repofolder.restrictedTraverse(
                '@@dossier_with_template/is_available')())

    def test_is_available_on_leaf_node_when_feature_is_enabled(self):
        self.login(self.regular_user)

        self.assertTrue(
            self.leaf_repofolder.restrictedTraverse(
                '@@dossier_with_template/is_available')())

    def test_is_not_available_if_user_does_not_have_add_dossier_permission(self):
        self.login(self.regular_user)
        self.set_workflow_state(
            'repositoryfolder-state-inactive', self.leaf_repofolder)

        self.assertFalse(
            api.user.has_permission(
                'opengever.dossier: Add businesscasedossier', obj=self.leaf_repofolder))

        self.assertFalse(
            self.leaf_repofolder.restrictedTraverse(
                '@@dossier_with_template/is_available')())

    def test_is_available_if_user_has_add_dossier_permission(self):
        self.login(self.regular_user)

        self.assertTrue(api.user.has_permission(
            'opengever.dossier: Add businesscasedossier', obj=self.leaf_repofolder))

        self.assertTrue(
            self.leaf_repofolder.restrictedTraverse(
                '@@dossier_with_template/is_available')())

    def test_is_not_available_if_businesscasedossier_disallowed(self):
        self.login(self.regular_user)

        self.leaf_repofolder.allow_add_businesscase_dossier = False

        self.assertFalse(
            self.leaf_repofolder.restrictedTraverse(
                '@@dossier_with_template/is_available')())

    def test_is_available_if_businesscasedossier_disallowed_but_addable_templates_selected(self):
        self.login(self.regular_user)

        self.leaf_repofolder.allow_add_businesscase_dossier = False

        self.set_related_items(
            self.leaf_repofolder, [self.dossiertemplate, ],
            fieldname='addable_dossier_templates')

        self.assertTrue(
            self.leaf_repofolder.restrictedTraverse(
                '@@dossier_with_template/is_available')())

    def test_raise_not_found_if_access_on_wizard_if_feature_is_not_available(self):
        self.login(self.regular_user)

        toggle_feature(IDossierTemplateSettings, enabled=False)

        with self.assertRaises(Unauthorized):
            self.leaf_repofolder.restrictedTraverse('@@dossier_with_template')()

        with self.assertRaises(Unauthorized):
            self.leaf_repofolder.restrictedTraverse('@@add-dossier-from-template')()

    @browsing
    def test_only_show_dossiertemplates_without_subdossiers(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.leaf_repofolder)
        factoriesmenu.add('Dossier with template')

        self.assertEqual(
            ['Bauvorhaben klein'],
            browser.css('.listing tr td:nth-child(2)').text)

    @browsing
    def test_selectable_templates_are_restricted_when_addable_templates_are_selected(self, browser):
        self.login(self.administrator, browser=browser)

        template = create(Builder("dossiertemplate")
                          .within(self.templates)
                          .titled(u"Bauvorhaben gross"))

        self.set_related_items(
            self.leaf_repofolder, [template, ],
            fieldname='addable_dossier_templates')

        self.login(self.regular_user, browser=browser)
        browser.open(self.leaf_repofolder)
        factoriesmenu.add('Dossier with template')

        self.assertEqual(
            ['Bauvorhaben gross'],
            browser.css('.listing tr td:nth-child(2)').text)

    @browsing
    def test_dossiertemplate_values_are_prefilled_properly_in_the_dossier(self, browser):

        self.login(self.regular_user, browser=browser)
        browser.open(self.leaf_repofolder)
        factoriesmenu.add('Dossier with template')

        token = browser.css(
            'input[name="form.widgets.template"]').first.attrib.get('value')
        browser.fill({'form.widgets.template': token}).submit()
        browser.click_on('Save')

        dossier = browser.context

        self.assertEqual('Bauvorhaben klein', dossier.title)
        self.assertEqual(u'Lorem ipsum', dossier.description)
        self.assertEqual((u'secret', u'special'), IDossier(dossier).keywords)
        self.assertEqual('this is very special', IDossier(dossier).comments)
        self.assertEqual('department', IDossier(dossier).filing_prefix)

    @browsing
    def test_dossiertemplate_do_not_copy_keywords(self, browser):
        self.login(self.regular_user, browser=browser)

        self.dossiertemplate.predefined_keywords = False

        browser.open(self.leaf_repofolder)
        factoriesmenu.add('Dossier with template')

        token = browser.css(
            'input[name="form.widgets.template"]').first.attrib.get('value')
        browser.fill({'form.widgets.template': token}).submit()
        browser.click_on('Save')

        self.assertEqual((), IDossier(browser.context).keywords)

    @browsing
    def test_dossiertemplate_restrict_keywords(self, browser):
        self.login(self.regular_user, browser=browser)

        self.dossiertemplate.restrict_keywords = True
        self.dossiertemplate.predefined_keywords = True

        browser.open(self.leaf_repofolder)
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

        self.assertItemsEqual([u'secret', u'special'], keywords.options_labels)
        browser.click_on('Save')
        self.assertItemsEqual((u'secret', u'special'),
                              IDossier(browser.context).keywords)

    @browsing
    def test_redirects_to_dossier_after_creating_dossier_from_template(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add('Dossier with template')

        token = browser.css(
            'input[name="form.widgets.template"]').first.attrib.get('value')
        browser.fill({'form.widgets.template': token}).submit()
        browser.click_on('Save')

        self.assertEqual(self.leaf_repofolder.listFolderContents()[-1],
                         browser.context)

    @browsing
    def test_redirects_to_first_step_if_the_user_skips_the_first_wizard_step(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.leaf_repofolder, view="add-dossier-from-template")

        self.assertEqual(
            '{}/dossier_with_template'.format(self.leaf_repofolder.absolute_url()),
            browser.url)

    @browsing
    def test_add_recursive_documents_and_subdossiers(self, browser):
        self.login(self.administrator, browser=browser)

        create(Builder('document')
               .titled('Document 1')
               .within(self.subdossiertemplate)
               .with_dummy_content())

        create(Builder("dossiertemplate")
               .within(self.subdossiertemplate)
               .titled(u'Anfragen 2017'))

        self.login(self.regular_user, browser=browser)
        browser.open(self.leaf_repofolder)
        factoriesmenu.add('Dossier with template')
        token = browser.css(
            'input[name="form.widgets.template"]').first.attrib.get('value')
        browser.fill({'form.widgets.template': token}).submit()
        browser.click_on('Save')

        dossier = browser.context

        self.assertEqual('Bauvorhaben klein', dossier.title)
        self.assertEqual(
            [u'Anfragen'],
            [obj.title for obj in dossier.listFolderContents()],
            "The content of the root-dossier is not correct."
            )

        subdossier = dossier.listFolderContents()[0]
        self.assertEqual(
            ['Document 1', u'Anfragen 2017'],
            [obj.title for obj in subdossier.listFolderContents()],
            "The content of the subdossiertemplate is not correct"
        )

    @browsing
    def test_subdossier_has_same_responsible_as_dossier(self, browser):
        self.login(self.regular_user, browser=browser)

        self.leaf_repofolder.restrictedTraverse(
            'add-dossier-from-template').form.recursive_content_creation

        browser.login().visit(self.leaf_repofolder)
        factoriesmenu.add('Dossier with template')
        token = browser.css(
            'input[name="form.widgets.template"]').first.attrib.get('value')
        browser.fill({'form.widgets.template': token}).submit()

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('peter.meier')

        browser.click_on('Save')

        subdossier = browser.context.listFolderContents()[0]

        self.assertEqual(self.dossier_responsible.getId(), IDossier(subdossier).responsible)

    @browsing
    def test_prefill_title_if_no_title_help_is_available(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add('Dossier with template')

        token = browser.css(
            'input[name="form.widgets.template"]').first.attrib.get('value')
        browser.fill({'form.widgets.template': token}).submit()

        self.assertEqual(
            "Bauvorhaben klein",
            browser.css('#formfield-form-widgets-IOpenGeverBase-title input').first.value)

        self.assertEqual(
            [], browser.css('#formfield-form-widgets-IOpenGeverBase-title .formHelp'))

    @browsing
    def test_do_not_fill_title_and_add_title_help_as_description_if_title_help_is_available(self, browser):
        self.login(self.regular_user, browser=browser)

        self.dossiertemplate.title_help = u"This is a help text"

        browser.open(self.leaf_repofolder)
        factoriesmenu.add('Dossier with template')

        token = browser.css(
            'input[name="form.widgets.template"]').first.attrib.get('value')
        browser.fill({'form.widgets.template': token}).submit()

        self.assertEqual(
            "",
            browser.css('#formfield-form-widgets-IOpenGeverBase-title input').first.value)

        self.assertEqual(
            "This is a help text",
            browser.css('#formfield-form-widgets-IOpenGeverBase-title .formHelp').first.text)


class TestSubDossierTemplateHandling(IntegrationTestCase):

    @browsing
    def test_max_dossier_depth_is_not_respected_by_default(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.subdossiertemplate)
        factoriesmenu.add('Subdossier')
        browser.fill({'Title': u'Sub Sub Template'}).submit()

        self.assertEquals(['Item created'], info_messages())
        self.assertEqual(u'Sub Sub Template', browser.context.title)

    @browsing
    def test_max_dossier_depth_is_respected_when_flag_is_activated(self, browser):
        self.login(self.administrator, browser=browser)

        api.portal.set_registry_record(
            'respect_max_depth', True, interface=IDossierTemplateSettings)

        browser.open(self.dossiertemplate)
        self.assertEqual(
            ['Document', 'Subdossier'], factoriesmenu.addable_types())

        browser.open(self.subdossiertemplate)
        self.assertEqual(['Document'], factoriesmenu.addable_types())

        # raise dossier depth
        api.portal.set_registry_record(
            'maximum_dossier_depth', 2, interface=IDossierContainerTypes)

        browser.open(self.subdossiertemplate)
        self.assertEqual(
            ['Document', 'Subdossier'], factoriesmenu.addable_types())


OVERVIEW_TAB = 'tabbedview_view-overview'
SUBDOSSIERS_TAB = 'tabbedview_view-subdossiers'
DOCUMENTS_LIST_TAB = 'tabbedview_view-documents'
DOCUMENTS_GALLERY_TAB = 'tabbedview_view-documents-gallery'


class TestDossierTemplateOverview(IntegrationTestCase):

    features = ('dossiertemplate', )

    @browsing
    def test_description_box_shows_description(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossiertemplate, view=OVERVIEW_TAB)

        self.assertEqual(u'Lorem ipsum',
                         browser.css('#descriptionBox span').first.text)

    @browsing
    def test_keywords_box_shows_keywords_as_list(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossiertemplate, view=OVERVIEW_TAB)

        self.assertEqual([u'secret', u'special'],
                         browser.css('#keywordsBox li span').text)

    @browsing
    def test_comments_box_shows_comment(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.dossiertemplate, view=OVERVIEW_TAB)
        self.assertEqual(u'this is very special',
                         browser.css('#commentsBox span').first.text)

    @browsing
    def test_filing_prefix_box_shows_filing_prefix_title(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.dossiertemplate, view=OVERVIEW_TAB)
        self.assertEqual(u'Department',
                         browser.css('#filing_prefixBox span').first.text)

    @browsing
    def test_document_box_items_are_limited_to_ten_and_sorted_by_sortable_title(self, browser):
        self.login(self.regular_user, browser=browser)

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

        browser.open(self.dossiertemplate, view=OVERVIEW_TAB)

        self.assertSequenceEqual(
            ['A Document', 'B Document', 'C Document 1', 'C Document 2', 'C Document 3',
             'C Document 4', 'C Document 5', 'C Document 6', 'C Document 7',
             'C Document 8'],
            browser.css('#documentsBox li:not(.moreLink) a.document_link').text)

    @browsing
    def test_documents_in_overview_are_linked(self, browser):
        self.login(self.regular_user, browser=browser)

        document = create(Builder('document')
                          .within(self.dossiertemplate)
                          .titled(u'Document 1'))

        browser.open(self.dossiertemplate, view=OVERVIEW_TAB)

        items = browser.css('#documentsBox li:not(.moreLink) a.document_link')

        self.assertEqual(1, len(items))
        self.assertEqual(document.absolute_url(), items.first.get('href'))


class TestDossierTemplateSubdossiers(IntegrationTestCase):

    features = ('dossiertemplate', )

    @browsing
    def test_list_subdossiers_alphabetically(self, browser):
        self.login(self.regular_user, browser=browser)

        create(Builder('dossiertemplate')
               .within(self.dossiertemplate)
               .titled(u'AA Subdossier'))

        create(Builder('dossiertemplate')
               .within(self.dossiertemplate)
               .titled(u'C Subdossier'))

        create(Builder('dossiertemplate')
               .within(self.dossiertemplate)
               .titled(u'B Subdossier'))

        browser.open(self.dossiertemplate, view=SUBDOSSIERS_TAB)

        self.assertEqual(
            ['AA Subdossier', 'Anfragen', 'B Subdossier', 'C Subdossier'],
            browser.css('table.listing a.contenttype-opengever-dossier-dossiertemplate').text)

    @browsing
    def test_list_subdossiers_in_subdossiers(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.dossiertemplate, view=SUBDOSSIERS_TAB)

        self.assertEqual(
            ['Anfragen'],
            browser.css('table.listing a.contenttype-opengever-dossier-dossiertemplate').text)


class TestDossierTemplateDocuments(IntegrationTestCase):

    features = ('dossiertemplate', 'bumblebee')

    def setUp(self):
        super(TestDossierTemplateDocuments, self).setUp()
        self.login(self.regular_user)

        create(Builder('document')
               .within(self.dossiertemplate)
               .titled('Document 1'))
        create(Builder('document')
               .within(self.dossiertemplate)
               .titled('Document 3'))
        create(Builder('document')
               .within(self.subdossiertemplate)
               .titled('Document 2'))

    @browsing
    def test_show_documents_in_list_view_sorted_alphabetically(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossiertemplate, view=DOCUMENTS_LIST_TAB)

        self.assertEqual(
            ['Document 1', 'Document 2', 'Document 3'],
            browser.css('table.listing a.icon-document_empty').text)

    @browsing
    def test_show_documents_in_gallery_view_sorted_alphabetically(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossiertemplate, view=DOCUMENTS_GALLERY_TAB)

        self.assertEqual(
            ['Document 1', 'Document 2', 'Document 3'],
            [preview.attrib.get('alt') for preview in browser.css(
                '.preview-listing .file-preview')])
