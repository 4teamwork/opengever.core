from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from plone import api
import json


class TestTranslatedTitlePost(IntegrationTestCase):

    @browsing
    def test_can_post_translated_title_for_inactive_lang(self, browser):
        language_tool = api.portal.get_tool('portal_languages')
        self.assertEqual(['en', 'de-ch'], language_tool.getSupportedLanguages())

        self.login(self.administrator, browser)
        data = {
            "@type": "opengever.repository.repositoryfolder",
            "title_de": "Folder",
            "title_fr": u"F\xf6lder",
        }

        with self.observe_children(self.repository_root) as children:
            browser.open(self.repository_root, json.dumps(data),
                         method="POST", headers=self.api_headers)

        self.assertEqual(1, len(children['added']))
        folder = children['added'].pop()
        self.assertEqual(u'F\xf6lder', folder.title_fr)

    @browsing
    def test_title_in_all_enabled_languages_is_required(self, browser):
        language_tool = api.portal.get_tool('portal_languages')
        language_tool.addSupportedLanguage('fr-ch')

        self.login(self.administrator, browser)
        data = {
            "@type": "opengever.repository.repositoryfolder",
            "title_de": "Folder",
        }

        with browser.expect_http_error(code=400, reason='Bad Request'):
            browser.open(self.repository_root, data=json.dumps(data),
                         method='POST', headers=self.api_headers)

        self.assertEqual(
            u"[{'field': 'title_fr', "
            "'message': u'Required input is missing.', "
            "'error': 'ValidationError'}]",
            browser.json['message'])


class TestTranslatedTitlePatch(IntegrationTestCase):

    @browsing
    def test_can_patch_translated_title_for_inactive_lang(self, browser):
        language_tool = api.portal.get_tool('portal_languages')
        self.assertEqual(['en', 'de-ch'], language_tool.getSupportedLanguages())

        self.login(self.administrator, browser)
        data = {
            "title_fr": u"F\xf6lder",
        }

        browser.open(self.empty_repofolder, json.dumps(data),
                     method="PATCH", headers=self.api_headers)

        self.assertEqual(u'F\xf6lder', self.empty_repofolder.title_fr)


class TestTranslatedTitleGet(IntegrationTestCase):

    @browsing
    def test_translated_title_not_serialized_for_inactive_lang(self, browser):
        language_tool = api.portal.get_tool('portal_languages')
        self.assertEqual(['en', 'de-ch'], language_tool.getSupportedLanguages())

        self.login(self.regular_user, browser)
        response = browser.open(self.empty_repofolder, method="GET",
                                headers=self.api_headers).json

        expected = {"title_de": u"Rechnungspr\xfcfungskommission"}
        self.assertDictContainsSubset(expected, response)
        self.assertNotIn("title_fr", response)

    @browsing
    def test_translated_title_serialized_for_all_active_langs(self, browser):
        language_tool = api.portal.get_tool('portal_languages')
        language_tool.addSupportedLanguage('fr-ch')

        self.login(self.regular_user, browser)
        response = browser.open(self.empty_repofolder, method="GET",
                                headers=self.api_headers).json

        expected = {
            "title_de": u"Rechnungspr\xfcfungskommission",
            "title_fr": u"Commission de v\xe9rification",
            }
        self.assertDictContainsSubset(expected, response)
