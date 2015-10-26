from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.testing import FunctionalTestCase
from opengever.testing import obj2brain
from plone import api
import transaction


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

    def test_translated_title_catalog_metadata(self):
        repository_root = create(Builder('repository_root')
                                 .having(title_de=u"Ablage",
                                         title_fr=u"syst\xe8me d'ordre"))

        brain = obj2brain(repository_root)
        self.assertEquals(u"Ablage", brain.title_de)
        self.assertEquals(u"syst\xe8me d'ordre", brain.title_fr)

    @browsing
    def test_both_title_fields_are_accessible_on_add_form(self, browser):
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

        browser.find('FR').click()
        self.assertEquals(u"syst\xe8me d'ordre", browser.css('h1').first.text)

        browser.find('DE').click()
        self.assertEquals("Ablage", browser.css('h1').first.text)

    @browsing
    def test_fallback_for_title_is_the_german_title(self, browser):
        repository_root = create(Builder('repository_root')
                                 .having(title_de=u"Ablage",
                                         title_fr=u"syst\xe8me d'ordre"))

        browser.login().open(repository_root)
        browser.find('English').click()
        self.assertEquals("Ablage", browser.css('h1').first.text)
