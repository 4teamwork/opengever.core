# -*- coding: utf-8 -*-

from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.base.behaviors.translated_title import ITranslatedTitle
from opengever.base.behaviors.translated_title import TRANSLATED_TITLE_NAMES
from opengever.base.behaviors.translated_title import TranslatedTitle
from opengever.base.brain import supports_translated_title
from opengever.testing import add_languages
from opengever.testing import FunctionalTestCase
from opengever.testing import obj2brain
from opengever.testing import set_preferred_language
from opengever.testing import TestCase
from plone import api
import transaction


class TestTranslatedTitleConfig(TestCase):

    def test_translated_title_config_is_consistent(self):
        self.assertEqual(len(TRANSLATED_TITLE_NAMES),
                         len(TranslatedTitle.SUPPORTED_LANGUAGES))

        names = ['title_{}'.format(code) for code in
                 TranslatedTitle.SUPPORTED_LANGUAGES]
        self.assertItemsEqual(names, TRANSLATED_TITLE_NAMES)

        self.assertItemsEqual(names, ITranslatedTitle.names())


class TestSupportTranslatedTitle(FunctionalTestCase):

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


class TestTranslatedTitle(FunctionalTestCase):

    def setUp(self):
        super(TestTranslatedTitle, self).setUp()
        self.grant('Administrator', 'Contributor')

        self.lang_tool = api.portal.get_tool('portal_languages')
        self.lang_tool.use_combined_language_codes = True
        self.lang_tool.addSupportedLanguage('de-ch')
        self.lang_tool.addSupportedLanguage('fr-ch')
        self.lang_tool.addSupportedLanguage('en')
        transaction.commit()

    @browsing
    def test_both_title_fields_are_accessible_on_add_form(self, browser):
        self.grant('Manager')
        browser.login().open()
        factoriesmenu.add('RepositoryRoot')

        browser.fill({"Title (German)": "Ablage",
                      "Title (French)": u"syst\xe8me d'ordre"})
        browser.find('Save').click()

        repository_root = browser.context
        self.assertEquals(u"Ablage", repository_root.title_de)
        self.assertEquals(u"syst\xe8me d'ordre", repository_root.title_fr)

    @browsing
    def test_both_title_fields_are_accessible_on_edit_form(self, browser):
        repository_root = create(Builder('repository_root')
                                 .having(title_de=u"Ablage",
                                         title_fr=u"syst\xe8me d'ordre"))

        browser.login().open(repository_root, view='edit')
        browser.fill({"Title (German)": "Ablage 1",
                      "Title (French)": u"syst\xe8me d'ordre 1"})
        browser.find('Save').click()

        self.assertEquals(u"Ablage 1", repository_root.title_de)
        self.assertEquals(u"syst\xe8me d'ordre 1", repository_root.title_fr)

    @browsing
    def test_Title_returns_title_in_preffered_language_by_default(self, browser):
        repository_root = create(Builder('repository_root')
                                 .having(title_de=u"Ablage",
                                         title_fr=u"syst\xe8me d'ordre"))

        browser.login().open(repository_root)

        browser.find(u'Français').click()
        self.assertEquals(u"syst\xe8me d'ordre", browser.css('h1').first.text)

        browser.find('Deutsch').click()
        self.assertEquals("Ablage", browser.css('h1').first.text)

    @browsing
    def test_translated_title_returns_title_in_asked_language(self, browser):
        repository_root = create(Builder('repository_root')
                                 .having(title_de=u"Ablage",
                                         title_fr=u"syst\xe8me d'ordre"))

        set_preferred_language(self.portal.REQUEST, 'de-ch')
        self.assertEquals(
            u"syst\xe8me d'ordre",
            ITranslatedTitle(repository_root).translated_title(language='fr'))

    @browsing
    def test_translated_title_returns_title_in_fallback_language_when_asked_language_not_supported(self, browser):
        repository_root = create(Builder('repository_root')
                                 .having(title_de=u"Ablage",
                                         title_fr=u"syst\xe8me d'ordre"))

        self.assertEquals(
            u"Ablage",
            ITranslatedTitle(repository_root).translated_title(language='it'))

    @browsing
    def test_fallback_for_title_is_the_german_title(self, browser):
        repository_root = create(Builder('repository_root')
                                 .having(title_de=u"Ablage",
                                         title_fr=u"syst\xe8me d'ordre"))

        browser.login().open(repository_root)
        browser.find('English').click()
        self.assertEquals("Ablage", browser.css('h1').first.text)

    def test_catalog_metadata(self):
        repository_root = create(Builder('repository_root')
                                 .having(title_de=u"Ablage",
                                         title_fr=u"syst\xe8me d'ordre"))

        brain = obj2brain(repository_root)
        self.assertEquals("Ablage", brain.title_de)
        self.assertEquals(u"syst\xe8me d'ordre", brain.title_fr)

    def test_indexer_returns_none_for_objects_without_translated_title_support(self):
        dossier = create(Builder('dossier')
                         .titled(u'Dossier A'))

        brain = obj2brain(dossier)
        self.assertEquals(None, brain.title_de)
        self.assertEquals(None, brain.title_fr)

    @browsing
    def test_Title_on_brains_returns_title_in_preferred_language(self, browser):
        repository_root = create(Builder('repository_root')
                                 .having(title_de=u"Ablage",
                                         title_fr=u"syst\xe8me d'ordre"))

        set_preferred_language(self.portal.REQUEST, 'fr-ch')

        self.assertEquals("syst\xc3\xa8me d'ordre",
                          obj2brain(repository_root).Title)

    @browsing
    def test_Title_on_brains_uses_Title_when_type_does_not_support_translated_title(self, browser):
        dossier = create(Builder('dossier').titled(u'F\xfchrung'))
        set_preferred_language(self.portal.REQUEST, 'de')
        self.assertEquals("F\xc3\xbchrung", obj2brain(dossier).Title)

        set_preferred_language(self.portal.REQUEST, 'fr')
        self.assertEquals("F\xc3\xbchrung", obj2brain(dossier).Title)


class TestTranslatedTitleAddForm(FunctionalTestCase):

    def setUp(self):
        super(TestTranslatedTitleAddForm, self).setUp()

        self.grant('Manager')

        add_languages('de-ch')
        add_languages('fr-ch')
        self.lang_tool = api.portal.get_tool('portal_languages')
        self.lang_tool.supported_langs = ['de-ch', 'fr-ch']
        transaction.commit()

    @browsing
    def test_language_fields_are_available_by_default(self, browser):
        browser.login().open(self.portal)
        factoriesmenu.add('RepositoryRoot')
        browser.fill({'Title (German)': u'Ordnungssystem',
                      u'Title (French)': u"syst\xe8me d'ordre"})
        browser.find('Save').click()

    @browsing
    def test_language_fields_of_inactive_languages_are_hidden(self, browser):
        self.lang_tool.supported_langs = ['fr-ch']
        transaction.commit()

        browser.login().open(self.portal)
        factoriesmenu.add('RepositoryRoot')

        self.assertEquals([u'Title', 'Valid from', 'Valid until', 'Version'],
                          browser.forms.get('form').css('label').text)
        self.assertEquals('form.widgets.ITranslatedTitle.title_fr',
                          browser.find_field_by_text('Title').get('name'))

        self.lang_tool.supported_langs = ['de-ch']
        transaction.commit()
        browser.login().open(self.portal)
        factoriesmenu.add('RepositoryRoot')

        self.assertEquals([u'Title', 'Valid from', 'Valid until', 'Version'],
                          browser.forms.get('form').css('label').text)
        self.assertEquals('form.widgets.ITranslatedTitle.title_de',
                          browser.find_field_by_text('Title').get('name'))

    @browsing
    def test_label_is_renamed_to_title_for_sites_with_only_one_active_language(self, browser):
        self.lang_tool.supported_langs = ['fr-ch']
        transaction.commit()

        browser.login().open(self.portal)
        factoriesmenu.add('RepositoryRoot')

        self.assertEquals(
            'Title',
            browser.css('label[for=form-widgets-ITranslatedTitle-title_fr]').first.text)


class TestTranslatedTitleEditForm(FunctionalTestCase):

    def setUp(self):
        super(TestTranslatedTitleEditForm, self).setUp()
        self.grant('Manager')
        self.lang_tool = api.portal.get_tool('portal_languages')

        self.repository_root = create(Builder('repository_root')
                                      .having(title_de=u"Ablage",
                                              title_fr=u"syst\xe8me d'ordre"))

    @browsing
    def test_language_fields_are_available_by_default(self, browser):
        self.lang_tool.supported_langs = ['de-ch', 'fr-ch']
        transaction.commit()

        browser.login().open(self.repository_root, view='edit')

        browser.fill({'Title (German)': u'Ordnungssystem',
                      u'Title (French)': u"syst\xe8me d'ordre"})
        browser.find('Save').click()

    @browsing
    def test_language_fields_of_inactive_languages_are_hidden(self, browser):
        self.lang_tool.supported_langs = ['fr-ch']
        transaction.commit()

        browser.login().open(self.repository_root, view='edit')
        self.assertEquals([u'Title', 'Valid from', 'Valid until', 'Version'],
                  browser.forms.get('form').css('label').text)
        self.assertEquals('form.widgets.ITranslatedTitle.title_fr',
                          browser.find_field_by_text('Title').get('name'))

    @browsing
    def test_label_is_renamed_to_title_for_sites_with_only_one_active_language(self, browser):
        self.lang_tool.supported_langs = ['fr-ch']
        transaction.commit()

        browser.login().open(self.repository_root, view='edit')
        self.assertEquals(
            'Title',
            browser.css('label[for=form-widgets-ITranslatedTitle-title_fr]').first.text)


class TestTranslatedTitleLanguageSupport(FunctionalTestCase):
    """A test which ensure that all language from the SUPPORTED_LANGUAGE
    constant is fully and correctly implemented.
    """

    def test_title_getter(self):
        titles = dict(
            (u'title_{}'.format(lang), u'Repository title in {}'.format(lang))
            for lang in TranslatedTitle.SUPPORTED_LANGUAGES)
        repository_root = create(Builder('repository_root')
                                 .having(**titles))

        for lang in TranslatedTitle.SUPPORTED_LANGUAGES:
            self.assertEquals(
                u"Repository title in {}".format(lang),
                getattr(ITranslatedTitle(repository_root), 'title_{}'.format(lang)))

    def test_title_setter(self):
        repository_root = create(Builder('repository_root'))

        for lang in TranslatedTitle.SUPPORTED_LANGUAGES:
            setattr(ITranslatedTitle(repository_root),
                    u'title_{}'.format(lang),
                    u'TITLE {}'.format(lang.upper()))

        for lang in TranslatedTitle.SUPPORTED_LANGUAGES:
            self.assertEquals(
                u'TITLE {}'.format(lang.upper()),
                getattr(ITranslatedTitle(repository_root), 'title_{}'.format(lang)))

    def test_all_catalog_metadata(self):
        titles = dict(
            (u'title_{}'.format(lang), u'Repository title in {}'.format(lang))
            for lang in TranslatedTitle.SUPPORTED_LANGUAGES)

        repository_root = create(Builder('repository_root')
                                 .having(**titles))

        brain = obj2brain(repository_root)
        for lang in TranslatedTitle.SUPPORTED_LANGUAGES:
            self.assertEquals(
                u"Repository title in {}".format(lang),
                getattr(brain, 'title_{}'.format(lang)))

    def test_translated_attribute_can_be_set_to_none(self):
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
