# -*- coding: utf-8 -*-

from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from opengever.base.behaviors.translated_title import ITranslatedTitle
from opengever.base.behaviors.translated_title import TRANSLATED_TITLE_NAMES
from opengever.base.behaviors.translated_title import TranslatedTitle
from opengever.base.brain import supports_translated_title
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2brain
from opengever.testing import set_preferred_language
from opengever.testing import TestCase
from plone import api


class TestTranslatedTitleIsOnTop(IntegrationTestCase):

    def assert_translated_title_fields_in_browser(self, browser):
        translated_fields = [
            'forms.widgets.ITranslatedTitle.title_{}'.format(lang)
            for lang in api.portal.get_tool('portal_languages').supported_langs
            if lang in TranslatedTitle.SUPPORTED_LANGUAGES
        ]

        first_fields = [
            _input.name
            for _input in browser.css("#form input[type!='hidden']")[:len(translated_fields)]
        ]
        self.assertEquals(translated_fields, first_fields)

    @browsing
    def test_translated_title_is_on_top_when_editing_the_inbox_container(
            self, browser):
        self.login(self.manager, browser=browser)

        inbox_container = create(Builder('inbox_container')
                                 .titled(u'Inboxes')
                                 .within(self.portal))

        browser.open(inbox_container, view='edit')
        statusmessages.assert_no_error_messages()

        self.assert_translated_title_fields_in_browser(browser)

    @browsing
    def test_translated_title_is_on_top_when_editing_the_private_root(
            self, browser):
        self.login(self.manager, browser=browser)

        browser.open(self.private_root, view='edit')
        statusmessages.assert_no_error_messages()

        self.assert_translated_title_fields_in_browser(browser)

    @browsing
    def test_translated_title_is_on_top_when_editing_the_inbox(self, browser):
        self.login(self.manager, browser=browser)

        browser.open(self.inbox, view='edit')
        statusmessages.assert_no_error_messages()

        self.assert_translated_title_fields_in_browser(browser)

    @browsing
    def test_translated_title_is_on_top_when_editing_the_committee_container(
            self, browser):
        self.login(self.manager, browser=browser)

        browser.open(self.committee_container, view='edit')
        statusmessages.assert_no_error_messages()

        self.assert_translated_title_fields_in_browser(browser)

    @browsing
    def test_translated_title_is_on_top_when_editing_the_templates(
            self, browser):
        self.login(self.manager, browser=browser)

        browser.open(self.templates, view='edit')
        statusmessages.assert_no_error_messages()

        self.assert_translated_title_fields_in_browser(browser)

    @browsing
    def test_translated_title_is_on_top_when_editing_the_workspace_root(
            self, browser):
        self.login(self.manager, browser=browser)

        browser.open(self.workspace_root, view='edit')
        statusmessages.assert_no_error_messages()

        self.assert_translated_title_fields_in_browser(browser)

    @browsing
    def test_translated_title_is_on_top_when_editing_the_repository_root(
            self, browser):
        self.login(self.manager, browser=browser)

        browser.open(self.repository_root, view='edit')
        statusmessages.assert_no_error_messages()

        self.assert_translated_title_fields_in_browser(browser)

    @browsing
    def test_translated_title_is_on_top_when_editing_the_contact_folder(
            self, browser):
        self.login(self.manager, browser=browser)

        browser.open(self.contactfolder, view='edit')
        statusmessages.assert_no_error_messages()

        self.assert_translated_title_fields_in_browser(browser)

    @browsing
    def test_translated_title_is_on_top_when_editing_the_repository_folder(
            self, browser):
        self.login(self.manager, browser=browser)

        browser.open(self.branch_repofolder, view='edit')
        statusmessages.assert_no_error_messages()

        self.assert_translated_title_fields_in_browser(browser)


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


class TestTranslatedTitle(IntegrationTestCase):

    def setUp(self):
        super(TestTranslatedTitle, self).setUp()
        self.enable_languages()

    @browsing
    def test_both_title_fields_are_accessible_on_add_form(self, browser):
        self.login(self.manager, browser=browser)

        browser.open(self.portal)
        factoriesmenu.add('RepositoryRoot')

        browser.fill({"Title (German)": "Ablage",
                      "Title (French)": u"syst\xe8me d'ordre"})
        browser.find('Save').click()

        repository_root = browser.context
        self.assertEquals(u"Ablage", repository_root.title_de)
        self.assertEquals(u"syst\xe8me d'ordre", repository_root.title_fr)

    @browsing
    def test_both_title_fields_are_accessible_on_edit_form(self, browser):
        self.login(self.manager, browser=browser)
        browser.open(self.repository_root, view='edit')
        browser.fill({"Title (German)": "Ablage 1",
                      "Title (French)": u"syst\xe8me d'ordre 1"})
        browser.find('Save').click()

        self.assertEquals(u"Ablage 1", self.repository_root.title_de)
        self.assertEquals(u"syst\xe8me d'ordre 1", self.repository_root.title_fr)

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
        browser.open(self.repository_root)
        browser.find('English').click()

        self.assertEquals("Ordnungssystem", browser.css('h1').first.text)

    def test_catalog_metadata(self):
        self.login(self.regular_user)

        brain = obj2brain(self.repository_root)
        self.assertEquals("Ordnungssystem", brain.title_de)
        self.assertEquals(u'Syst\xe8me de classement', brain.title_fr)

    def test_indexer_returns_none_for_objects_without_translated_title_support(self):
        self.login(self.regular_user)

        brain = obj2brain(self.dossier)
        self.assertEquals(None, brain.title_de)
        self.assertEquals(None, brain.title_fr)

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


class TestTranslatedTitleAddForm(IntegrationTestCase):

    def setUp(self):
        super(TestTranslatedTitleAddForm, self).setUp()
        self.enable_languages()
        self.lang_tool = api.portal.get_tool('portal_languages')

    @browsing
    def test_language_fields_are_available_by_default(self, browser):
        self.login(self.manager, browser=browser)

        browser.open(self.portal)
        factoriesmenu.add('RepositoryRoot')

        browser.fill({'Title (German)': u'Ordnungssystem',
                      u'Title (French)': u"syst\xe8me d'ordre"})
        browser.find('Save').click()

    @browsing
    def test_language_fields_of_inactive_languages_are_hidden(self, browser):
        self.login(self.manager, browser=browser)

        self.lang_tool.supported_langs = ['fr-ch']
        browser.open(self.portal)
        factoriesmenu.add('RepositoryRoot')

        self.assertEquals([u'Title', 'Valid from', 'Valid until', 'Version'],
                          browser.forms.get('form').css('label').text)
        self.assertEquals('form.widgets.ITranslatedTitle.title_fr',
                          browser.find_field_by_text('Title').get('name'))

        self.lang_tool.supported_langs = ['de-ch']
        browser.open(self.portal)
        factoriesmenu.add('RepositoryRoot')

        self.assertEquals([u'Title', 'Valid from', 'Valid until', 'Version'],
                          browser.forms.get('form').css('label').text)
        self.assertEquals('form.widgets.ITranslatedTitle.title_de',
                          browser.find_field_by_text('Title').get('name'))

    @browsing
    def test_label_is_renamed_to_title_for_sites_with_only_one_active_language(self, browser):
        self.login(self.manager, browser=browser)

        self.lang_tool.supported_langs = ['fr-ch']

        browser.open(self.portal)
        factoriesmenu.add('RepositoryRoot')

        self.assertEquals(
            'Title',
            browser.css('label[for=form-widgets-ITranslatedTitle-title_fr]').first.text)


class TestTranslatedTitleEditForm(IntegrationTestCase):

    def setUp(self):
        super(TestTranslatedTitleEditForm, self).setUp()
        self.enable_languages()
        self.lang_tool = api.portal.get_tool('portal_languages')

    @browsing
    def test_language_fields_are_available_by_default(self, browser):
        self.login(self.manager, browser=browser)

        self.lang_tool.supported_langs = ['de-ch', 'fr-ch']

        browser.open(self.repository_root, view='edit')

        browser.fill({'Title (German)': u'Ordnungssystem',
                      u'Title (French)': u"syst\xe8me d'ordre"})
        browser.find('Save').click()

    @browsing
    def test_language_fields_of_inactive_languages_are_hidden(self, browser):
        self.login(self.manager, browser=browser)

        self.lang_tool.supported_langs = ['fr-ch']

        browser.open(self.repository_root, view='edit')
        self.assertEquals([u'Title', 'Valid from', 'Valid until', 'Version'],
                          browser.forms.get('form').css('label').text)
        self.assertEquals('form.widgets.ITranslatedTitle.title_fr',
                          browser.find_field_by_text('Title').get('name'))

    @browsing
    def test_label_is_renamed_to_title_for_sites_with_only_one_active_language(self, browser):
        self.login(self.manager, browser=browser)

        self.lang_tool.supported_langs = ['fr-ch']

        browser.open(self.repository_root, view='edit')
        self.assertEquals(
            'Title',
            browser.css('label[for=form-widgets-ITranslatedTitle-title_fr]').first.text)


class TestTranslatedTitleLanguageSupport(IntegrationTestCase):
    """A test which ensure that all language from the SUPPORTED_LANGUAGE
    constant is fully and correctly implemented.
    """

    titles = dict(de=u'Ordnungssystem',
                  fr=u'Syst\xe8me de classement')

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
