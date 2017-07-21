from ftw.testbrowser import browser
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from plone import api
from plone.restapi.permissions import UseRESTAPI
import json
import transaction


class Testi18nService(FunctionalTestCase):

    def setUp(self):
        super(Testi18nService, self).setUp()
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.supported_langs = ['en', 'de-ch', 'fr-ch']
        self.portal.manage_permission(UseRESTAPI, roles=['Authenticated'])
        transaction.commit()

    def set_lang(self, code):
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage(code)
        transaction.commit()

    def get_translations(self):
        browser.login().open(view='@i18n', headers={'Accept': 'application/json'})
        return json.loads(browser.json)

    @browsing
    def test_get_translations(self, browser):
        self.assertDictContainsSubset({
                u'label_add_to_favorites':
                u'Add to favorites',
            },
            self.get_translations())

    @browsing
    def test_get_translations_german(self, browser):
        self.set_lang('de-ch')

        self.assertDictContainsSubset({
                u'label_add_to_favorites':
                u'Als Favorit markieren',
            },
            self.get_translations())

    @browsing
    def test_get_translations_french(self, browser):
        self.set_lang('fr-ch')

        self.assertDictContainsSubset({
                u'label_add_to_favorites': u'Ajouter aux favoris',
            },
            self.get_translations())
