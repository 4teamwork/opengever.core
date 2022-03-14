# -*- coding: utf-8 -*-
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from opengever.base.behaviors.translated_title import get_active_languages
from opengever.base.behaviors.translated_title import get_inactive_languages
from opengever.base.behaviors.translated_title import has_translation_behavior
from opengever.base.behaviors.translated_title import ITranslatedTitle
from opengever.base.behaviors.translated_title import TRANSLATED_TITLE_NAMES
from opengever.base.behaviors.translated_title import TRANSLATED_TITLE_PORTAL_TYPES
from opengever.base.behaviors.translated_title import TranslatedTitle
from opengever.base.brain import supports_translated_title
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2brain
from opengever.testing import set_preferred_language
from opengever.testing import solr_data_for
from opengever.testing import SolrIntegrationTestCase
from opengever.testing import TestCase
from plone import api


class TestTranslatedTitleActiveLanguages(IntegrationTestCase):

    def test_get_active_languages_default(self):
        self.assertEqual(['en', 'de'], get_active_languages())

    def test_get_active_languages_all_supported_enabled(self):
        language_tool = api.portal.get_tool('portal_languages')
        language_tool.addSupportedLanguage('fr-ch')
        self.assertEqual(['en', 'de', 'fr'], get_active_languages())


class TestTranslatedTitleInactiveLanguages(IntegrationTestCase):

    def test_get_active_languages_default(self):
        self.assertEqual(['fr'], get_inactive_languages())

    def test_get_active_languages_all_supported_enabled(self):
        language_tool = api.portal.get_tool('portal_languages')
        language_tool.addSupportedLanguage('fr-ch')
        self.assertEqual([], get_inactive_languages())


class TestTranslatedTitleHasTranslationBehavior(IntegrationTestCase):

    def test_has_translation_behavior(self):
        ttool = api.portal.get_tool("portal_types")

        self.assertFalse(has_translation_behavior(
            ttool["Plone Site"]))
        self.assertFalse(has_translation_behavior(
            ttool["opengever.document.document"]))

        self.assertTrue(has_translation_behavior(
            ttool["opengever.repository.repositoryfolder"]))
        self.assertTrue(has_translation_behavior(
            ttool["opengever.contact.contactfolder"]))


class TestTranslatedTitleBehavior(IntegrationTestCase):

    def test_translated_title_portal_types_list_is_complete(self):
        types_tool = api.portal.get_tool('portal_types')
        types_with_behavior = [
            portal_type for portal_type, fti in types_tool.items()
            if has_translation_behavior(fti)]
        self.assertItemsEqual(TRANSLATED_TITLE_PORTAL_TYPES,
                              types_with_behavior)


class TranslatedTitleTestMixin(object):

    def assert_expected_translated_title_fields_are_displayed_in_browser(
            self, browser, expected_languages):
        """Make sure that only fields corresponding to the expected languages
        are shown. We also check that they are displayed at the top of the form.
        """
        expected_fields = [
            'form.widgets.ITranslatedTitle.title_{}'.format(lang)
            for lang in expected_languages]

        first_fields = [
            _input.name for _input in browser.css(
                "#form input[type!='hidden']")[:len(expected_fields)]]

        actual_fields = [
            _input.name for _input in browser.css("#form input[type!='hidden']")
            if _input.name and 'form.widgets.ITranslatedTitle' in _input.name]

        self.assertEqual(expected_fields, actual_fields)
        self.assertEqual(
            actual_fields, first_fields,
            "Translated title fields should come at the top of the form")


class TestTranslatedTitleFieldsInEditForms(IntegrationTestCase, TranslatedTitleTestMixin):

    def assert_edit_form_shows_translated_title_fields_only_for_active_languages(
            self, browser, obj):
        lang_tool = api.portal.get_tool('portal_languages')
        self.assertItemsEqual(['en', 'de-ch'], lang_tool.supported_langs)

        browser.open(obj, view='edit')
        statusmessages.assert_no_error_messages()
        self.assert_expected_translated_title_fields_are_displayed_in_browser(
            browser, ['de', 'en'])

        lang_tool.addSupportedLanguage('fr-ch')

        browser.open(obj, view='edit')
        statusmessages.assert_no_error_messages()
        self.assert_expected_translated_title_fields_are_displayed_in_browser(
            browser, ['de', 'fr', 'en'])

    @browsing
    def test_modifying_language_fields_in_edit_form(self, browser):
        self.login(self.manager, browser=browser)
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.supported_langs = ['de-ch', 'fr-ch']

        browser.open(self.repository_root, view='edit')

        browser.fill({'Title (German)': u'Ordnungssystem',
                      u'Title (French)': u"syst\xe8me d'ordre"})
        browser.find('Save').click()

    @browsing
    def test_label_is_renamed_to_title_for_sites_with_only_one_active_language(self, browser):
        self.login(self.manager, browser=browser)
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.supported_langs = ['de-ch', 'fr-ch']

        browser.open(self.repository_root, view='edit')
        self.assertEquals(
            'Title (French)',
            browser.css('label[for=form-widgets-ITranslatedTitle-title_fr]').first.text)

        lang_tool.supported_langs = ['fr-ch']

        browser.open(self.repository_root, view='edit')
        self.assertEquals(
            'Title',
            browser.css('label[for=form-widgets-ITranslatedTitle-title_fr]').first.text)

    @browsing
    def test_inbox_container_edit_form_only_shows_translated_title_fields_for_active_languages(
            self, browser):
        self.login(self.manager, browser=browser)
        self.assert_edit_form_shows_translated_title_fields_only_for_active_languages(
            browser, self.inbox_container)

    @browsing
    def test_private_root_edit_form_only_shows_translated_title_fields_for_active_languages(
            self, browser):
        self.login(self.manager, browser=browser)
        self.assert_edit_form_shows_translated_title_fields_only_for_active_languages(
            browser, self.private_root)

    @browsing
    def test_inbox_edit_form_only_shows_translated_title_fields_for_active_languages(self, browser):
        self.login(self.manager, browser=browser)
        self.assert_edit_form_shows_translated_title_fields_only_for_active_languages(
            browser, self.inbox)

    @browsing
    def test_committee_container_edit_form_only_shows_translated_title_fields_for_active_languages(
            self, browser):
        self.login(self.manager, browser=browser)
        self.assert_edit_form_shows_translated_title_fields_only_for_active_languages(
            browser, self.committee_container)

    @browsing
    def test_template_folder_edit_form_only_shows_translated_title_fields_for_active_languages(
            self, browser):
        self.login(self.manager, browser=browser)
        self.assert_edit_form_shows_translated_title_fields_only_for_active_languages(
            browser, self.templates)

    @browsing
    def test_workspace_root_edit_form_only_shows_translated_title_fields_for_active_languages(
            self, browser):
        self.login(self.manager, browser=browser)
        self.assert_edit_form_shows_translated_title_fields_only_for_active_languages(
            browser, self.workspace_root)

    @browsing
    def test_repository_root_edit_form_only_shows_translated_title_fields_for_active_languages(
            self, browser):
        self.login(self.manager, browser=browser)
        self.assert_edit_form_shows_translated_title_fields_only_for_active_languages(
            browser, self.repository_root)

    @browsing
    def test_contact_folder_edit_form_only_shows_translated_title_fields_for_active_languages(
            self, browser):
        self.login(self.manager, browser=browser)
        self.assert_edit_form_shows_translated_title_fields_only_for_active_languages(
            browser, self.contactfolder)

    @browsing
    def test_repository_folder_edit_form_only_shows_translated_title_fields_for_active_languages(
            self, browser):
        self.login(self.manager, browser=browser)
        self.assert_edit_form_shows_translated_title_fields_only_for_active_languages(
            browser, self.branch_repofolder)


class TestTranslatedTitleConfig(TestCase):

    def test_translated_title_config_is_consistent(self):
        self.assertEqual(len(TRANSLATED_TITLE_NAMES),
                         len(TranslatedTitle.SUPPORTED_LANGUAGES))

        names = ['title_{}'.format(code) for code in
                 TranslatedTitle.SUPPORTED_LANGUAGES]
        self.assertItemsEqual(names, TRANSLATED_TITLE_NAMES)

        self.assertItemsEqual(names, ITranslatedTitle.names())


class TestSupportTranslatedTitle(IntegrationTestCase):

    def test_repositories_supports_translated_title(self):
        self.assertTrue(
            supports_translated_title('opengever.repository.repositoryfolder'))

    def test_portal_objects_supports_translated_title(self):
        self.assertTrue(
            supports_translated_title('opengever.repository.repositoryroot'))
        self.assertTrue(
            supports_translated_title('opengever.inbox.inbox'))
        self.assertTrue(
            supports_translated_title('opengever.contact.contactfolder'))
        self.assertTrue(
            supports_translated_title('opengever.dossier.templatefolder'))

    def test_content_objects_does_not_support_translated_title(self):
        self.assertFalse(
            supports_translated_title('opengever.dossier.businesscasedossier'))
        self.assertFalse(
            supports_translated_title('opengever.document.document'))
        self.assertFalse(
            supports_translated_title('ftw.mail.mail'))
        self.assertFalse(
            supports_translated_title('opengever.contact.contact'))


class TestTranslatedTitle(SolrIntegrationTestCase):

    def setUp(self):
        super(TestTranslatedTitle, self).setUp()
        self.enable_languages()

    @browsing
    def test_all_title_fields_are_accessible_on_add_form(self, browser):
        self.login(self.manager, browser=browser)

        browser.open(self.portal)
        factoriesmenu.add('Repository Root')

        browser.fill({"Title (German)": "Ablage",
                      "Title (French)": u"Syst\xe8me de classement",
                      "Title (English)": u"Repository root"})
        browser.find('Save').click()
        statusmessages.assert_no_error_messages()

        repository_root = browser.context
        self.assertEquals(u"Ablage", repository_root.title_de)
        self.assertEquals(u"Syst\xe8me de classement", repository_root.title_fr)
        self.assertEquals(u"Repository root", repository_root.title_en)

    @browsing
    def test_all_title_fields_are_accessible_on_edit_form(self, browser):
        self.login(self.manager, browser=browser)
        browser.open(self.repository_root, view='edit')
        browser.fill({"Title (German)": "Ablage 1",
                      "Title (French)": u"Syst\xe8me de classement 1",
                      "Title (English)": u"Repository root 1"})
        browser.find('Save').click()
        statusmessages.assert_no_error_messages()

        self.assertEquals(u"Ablage 1", self.repository_root.title_de)
        self.assertEquals(u"Syst\xe8me de classement 1", self.repository_root.title_fr)
        self.assertEquals(u"Repository root 1", self.repository_root.title_en)

    @browsing
    def test_Title_returns_title_in_preffered_language_by_default(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.repository_root)

        browser.find(u'Français').click()
        self.assertEquals(u"Syst\xe8me de classement", browser.css('h1').first.text)

        browser.find('Deutsch').click()
        self.assertEquals("Ordnungssystem", browser.css('h1').first.text)

    @browsing
    def test_translated_title_returns_title_in_asked_language(self, browser):
        self.login(self.regular_user, browser=browser)

        set_preferred_language(self.portal.REQUEST, 'de-ch')

        self.assertEquals(
            u"Syst\xe8me de classement",
            ITranslatedTitle(self.repository_root).translated_title(language='fr'))

    @browsing
    def test_translated_title_returns_title_in_fallback_language_when_asked_language_not_supported(self, browser):
        self.login(self.regular_user, browser=browser)

        self.assertEquals(
            u"Ordnungssystem",
            ITranslatedTitle(self.repository_root).translated_title(language='it'))

    @browsing
    def test_fallback_for_title_is_the_german_title(self, browser):
        self.login(self.regular_user, browser=browser)
        self.repository_root.title_en = ''
        browser.open(self.repository_root)
        browser.find('English').click()

        self.assertEquals("Ordnungssystem", browser.css('h1').first.text)

    def test_catalog_metadata(self):
        self.login(self.regular_user)

        brain = obj2brain(self.repository_root)
        self.assertEquals(u"Ordnungssystem", brain.title_de)
        self.assertEquals(u'Syst\xe8me de classement', brain.title_fr)
        self.assertEquals(u"Ordnungssystem", brain.title_en)

        self.repository_root.title_en = "Repository"
        self.repository_root.reindexObject()
        brain = obj2brain(self.repository_root)
        self.assertEquals(u"Ordnungssystem", brain.title_de)
        self.assertEquals(u'Syst\xe8me de classement', brain.title_fr)
        self.assertEquals('Repository', brain.title_en)

    def test_solr_stored_values(self):
        self.login(self.regular_user)

        solr_data = solr_data_for(self.repository_root)
        self.assertEquals(u"Ordnungssystem", solr_data['title_de'])
        self.assertEquals(u'Syst\xe8me de classement', solr_data['title_fr'])
        self.assertEquals(u"Ordnungssystem", solr_data['title_en'])

        self.repository_root.title_en = "Repository"
        self.repository_root.reindexObject()
        self.commit_solr()

        solr_data = solr_data_for(self.repository_root)
        self.assertEquals(u"Ordnungssystem", solr_data['title_de'])
        self.assertEquals(u'Syst\xe8me de classement', solr_data['title_fr'])
        self.assertEquals('Repository', solr_data['title_en'])

    def test_indexer_returns_none_for_objects_without_translated_title_support(self):
        self.login(self.regular_user)

        brain = obj2brain(self.dossier)
        self.assertEquals(None, brain.title_de)
        self.assertEquals(None, brain.title_fr)
        self.assertEquals(None, brain.title_en)

    def test_solr_data_doesnt_contain_keys_for_objects_without_translated_title_support(self):
        self.login(self.regular_user)

        solr_data = solr_data_for(self.dossier)
        self.assertNotIn('title_de', solr_data)
        self.assertNotIn('title_fr', solr_data)
        self.assertNotIn('title_en', solr_data)

    @browsing
    def test_Title_on_brains_returns_title_in_preferred_language(self, browser):
        self.login(self.regular_user)

        set_preferred_language(self.portal.REQUEST, 'fr-ch')

        self.assertEquals('Syst\xc3\xa8me de classement',
                          obj2brain(self.repository_root).Title)

    @browsing
    def test_Title_on_brains_uses_Title_when_type_does_not_support_translated_title(self, browser):
        self.login(self.regular_user)

        set_preferred_language(self.portal.REQUEST, 'de-ch')
        self.assertEquals('Vertr\xc3\xa4ge mit der kantonalen Finanzverwaltung',
                          obj2brain(self.dossier).Title)

        set_preferred_language(self.portal.REQUEST, 'fr-ch')
        self.assertEquals('Vertr\xc3\xa4ge mit der kantonalen Finanzverwaltung',
                          obj2brain(self.dossier).Title)


class TestTranslatedTitleAddForm(IntegrationTestCase, TranslatedTitleTestMixin):

    def setUp(self):
        super(TestTranslatedTitleAddForm, self).setUp()
        self.lang_tool = api.portal.get_tool('portal_languages')

    def assert_add_form_shows_translated_title_fields_only_for_active_languages(
            self, browser, container, portal_type):
        self.assertItemsEqual(['en', 'de-ch'], self.lang_tool.supported_langs)

        browser.open(container)
        factoriesmenu.add(portal_type)
        statusmessages.assert_no_error_messages()
        self.assert_expected_translated_title_fields_are_displayed_in_browser(
            browser, ['de', 'en'])

        self.lang_tool.addSupportedLanguage('fr-ch')

        browser.open(container)
        factoriesmenu.add(portal_type)
        statusmessages.assert_no_error_messages()
        self.assert_expected_translated_title_fields_are_displayed_in_browser(
            browser, ['de', 'fr', 'en'])

    @browsing
    def test_setting_language_fields_in_add_form(self, browser):
        self.login(self.manager, browser=browser)

        self.lang_tool.supported_langs = ['de-ch', 'fr-ch']

        with self.observe_children(self.portal) as children:
            browser.open(self.portal)
            factoriesmenu.add('Repository Root')

            browser.fill({'Title (German)': u'Ordnungssystem',
                          u'Title (French)': u"syst\xe8me de classement"})
            browser.find('Save').click()

        self.assertEqual(1, len(children['added']))
        repo_root = children['added'].pop()
        self.assertEqual(u'Ordnungssystem', repo_root.title_de)
        self.assertEqual(u"syst\xe8me de classement", repo_root.title_fr)

    @browsing
    def test_label_is_renamed_to_title_for_sites_with_only_one_active_language(self, browser):
        self.login(self.manager, browser=browser)
        self.lang_tool.supported_langs = ['de-ch', 'fr-ch']

        browser.open(self.portal)
        factoriesmenu.add('Repository Root')
        self.assertEquals(
            'Title (French)',
            browser.css('label[for=form-widgets-ITranslatedTitle-title_fr]').first.text)

        self.lang_tool.supported_langs = ['fr-ch']

        browser.open(self.portal)
        factoriesmenu.add('Repository Root')
        self.assertEquals(
            'Title',
            browser.css('label[for=form-widgets-ITranslatedTitle-title_fr]').first.text)

    @browsing
    def test_inbox_container_add_form_only_shows_translated_title_fields_for_active_languages(
            self, browser):
        self.login(self.manager, browser=browser)
        self.assert_add_form_shows_translated_title_fields_only_for_active_languages(
            browser, self.portal, 'Inbox Container')

    @browsing
    def test_private_root_add_form_only_shows_translated_title_fields_for_active_languages(
            self, browser):
        self.login(self.manager, browser=browser)
        self.assert_add_form_shows_translated_title_fields_only_for_active_languages(
            browser, self.portal, 'Private Root')

    @browsing
    def test_inbox_add_form_only_shows_translated_title_fields_for_active_languages(
            self, browser):
        self.login(self.manager, browser=browser)

        self.assertItemsEqual(['en', 'de-ch'], self.lang_tool.supported_langs)

        browser.open(self.inbox_container, view='++add++opengever.inbox.inbox')
        statusmessages.assert_no_error_messages()
        self.assert_expected_translated_title_fields_are_displayed_in_browser(
            browser, ['de', 'en'])

        self.lang_tool.addSupportedLanguage('fr-ch')

        browser.open(self.inbox_container, view='++add++opengever.inbox.inbox')
        statusmessages.assert_no_error_messages()
        self.assert_expected_translated_title_fields_are_displayed_in_browser(
            browser, ['de', 'fr', 'en'])

    @browsing
    def test_committee_container_add_form_only_shows_translated_title_fields_for_active_languages(
            self, browser):
        self.activate_feature('meeting')
        self.login(self.manager, browser=browser)
        self.assert_add_form_shows_translated_title_fields_only_for_active_languages(
            browser, self.portal, 'Committee Container')

    @browsing
    def test_template_folder_add_form_only_shows_translated_title_fields_for_active_languages(
            self, browser):
        self.login(self.manager, browser=browser)
        self.assert_add_form_shows_translated_title_fields_only_for_active_languages(
            browser, self.portal, 'Template Folder')

    @browsing
    def test_workspace_root_add_form_only_shows_translated_title_fields_for_active_languages(
            self, browser):
        self.login(self.manager, browser=browser)
        self.assert_add_form_shows_translated_title_fields_only_for_active_languages(
            browser, self.portal, 'Workspace Root')

    @browsing
    def test_repository_root_add_form_only_shows_translated_title_fields_for_active_languages(
            self, browser):
        self.login(self.manager, browser=browser)
        self.assert_add_form_shows_translated_title_fields_only_for_active_languages(
            browser, self.portal, 'Repository Root')

    @browsing
    def test_contact_folder_add_form_only_shows_translated_title_fields_for_active_languages(
            self, browser):
        self.login(self.manager, browser=browser)
        self.assert_add_form_shows_translated_title_fields_only_for_active_languages(
            browser, self.portal, 'Contact Folder')

    @browsing
    def test_repository_folder_add_form_only_shows_translated_title_fields_for_active_languages(
            self, browser):
        self.login(self.manager, browser=browser)
        self.assert_add_form_shows_translated_title_fields_only_for_active_languages(
            browser, self.repository_root, 'Repository Folder')


class TestTranslatedTitleLanguageSupport(SolrIntegrationTestCase):
    """A test which ensure that all language from the SUPPORTED_LANGUAGE
    constant is fully and correctly implemented.
    """

    titles = dict(de=u'Ordnungssystem',
                  fr=u'Syst\xe8me de classement',
                  en=u'Ordnungssystem')

    def test_title_getter(self):
        self.login(self.manager)

        for lang in TranslatedTitle.SUPPORTED_LANGUAGES:
            self.assertEquals(
                self.titles[lang],
                getattr(ITranslatedTitle(self.repository_root),
                        'title_{}'.format(lang)))

    def test_title_setter(self):
        self.login(self.manager)

        for lang in TranslatedTitle.SUPPORTED_LANGUAGES:
            setattr(ITranslatedTitle(self.repository_root),
                    u'title_{}'.format(lang),
                    self.titles[lang].upper())

        for lang in TranslatedTitle.SUPPORTED_LANGUAGES:
            self.assertEquals(
                self.titles[lang].upper(),
                getattr(ITranslatedTitle(self.repository_root),
                        'title_{}'.format(lang)))

    def test_all_catalog_metadata(self):
        self.login(self.manager)

        brain = obj2brain(self.repository_root)
        for lang in TranslatedTitle.SUPPORTED_LANGUAGES:
            self.assertEquals(
                self.titles[lang],
                getattr(brain, 'title_{}'.format(lang)))

    def test_all_solr_stored_values(self):
        self.login(self.manager)

        solr_data = solr_data_for(self.repository_root)
        for lang in TranslatedTitle.SUPPORTED_LANGUAGES:
            self.assertEquals(
                self.titles[lang],
                solr_data['title_{}'.format(lang)])

    def test_translated_attribute_can_be_set_to_none(self):
        self.login(self.manager)

        repository_root = create(Builder('repository_root')
                                 .having(title_de=u"Ablage",
                                         title_fr=u"syst\xe8me d'ordre"))
        root_translation = ITranslatedTitle(repository_root)

        repository_root.title_de = None
        repository_root.title_fr = None

        self.assertIsNone(root_translation.translated_title())
        self.assertIsNone(root_translation.translated_title(language='de'))
        self.assertIsNone(root_translation.translated_title(language='fr'))

        self.assertEqual('', repository_root.Title())
        self.assertEqual('', repository_root.Title(language='de'))
        self.assertEqual('', repository_root.Title(language='fr'))
