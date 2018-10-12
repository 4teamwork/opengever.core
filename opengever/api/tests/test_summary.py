# -*- coding: utf-8 -*-
from ftw.testbrowser import browsing
from opengever.api.testing import RelativeSession
from opengever.testing import IntegrationTestCase
from plone import api
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD


class TestGeverJSONSummarySerializer(IntegrationTestCase):

    def setUp(self):
        super(TestGeverJSONSummarySerializer, self).setUp()

        self.api = RelativeSession(self.portal.absolute_url())
        self.api.headers.update({'Accept': 'application/json'})
        self.api.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de-ch')
        lang_tool.supported_langs = ['fr-ch', 'de-ch']

    @browsing
    def test_portal_type_is_included(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.repository_root.absolute_url(),
            headers={'Accept': 'application/json'})
        repofolder_summary = browser.json['items'][0]

        self.assertDictContainsSubset(
            {u'@type': u'opengever.repository.repositoryfolder'},
            repofolder_summary)

        browser.open(
            self.leaf_repofolder.absolute_url(),
            headers={'Accept': 'application/json'})
        dossier_summary = browser.json['items'][0]

        self.assertDictContainsSubset(
            {u'@type': u'opengever.dossier.businesscasedossier'},
            dossier_summary)

    @browsing
    def test_translated_title_contained_in_summary_if_obj_translated(
            self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.repository_root.absolute_url(),
            headers={'Accept': 'application/json', 'Accept-Language': 'de-ch'})
        repofolder_summary = browser.json['items'][0]

        self.assertDictContainsSubset(
            {u'title': u'1. Führung'},
            repofolder_summary)

        browser.open(
            self.repository_root.absolute_url(),
            headers={'Accept': 'application/json', 'Accept-Language': 'fr-ch'})
        repofolder_summary = browser.json['items'][0]

        self.assertDictContainsSubset(
            {u'title': u'1. Direction'},
            repofolder_summary)

    @browsing
    def test_translated_titles_default_to_german(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.repository_root.absolute_url(),
            headers={'Accept': 'application/json'})
        repofolder_summary = browser.json['items'][0]

        self.assertDictContainsSubset(
            {u'title': u'1. Führung'},
            repofolder_summary)

    @browsing
    def test_regular_title_in_summary_if_obj_not_translated(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.leaf_repofolder.absolute_url(),
            headers={'Accept': 'application/json'})
        dossier_summary = browser.json['items'][0]

        self.assertDictContainsSubset(
            {u'title': u'Verträge mit der kantonalen Finanzverwaltung'},
            dossier_summary)

    @browsing
    def test_summary_with_custom_field_list(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier.absolute_url() +
            '?items.fl=filesize,filename,modified,created,mimetype,creator,changed',
            headers={'Accept': 'application/json'})

        summary = browser.json['items'][0]
        self.assertEqual(
            {
                u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-'
                u'und-vereinbarungen/dossier-1/document-12',
                u'changed': u'2016-08-31T13:07:33+00:00',
                u'created': u'2016-08-31T13:07:33+00:00',
                u'creator': u'robert.ziegler',
                u'filename': u'Vertraegsentwurf.docx',
                u'filesize': 27413,
                u'mimetype': u'application/vnd.openxmlformats-officedocument.'
                u'wordprocessingml.document',
                u'modified': u'2016-08-31T13:07:33+00:00'},
            summary)

    @browsing
    def test_summary_with_reference_number(self, browser):
        self.login(self.regular_user, browser)
        browser.open(
            self.dossier.absolute_url() +
            '?items.fl=reference_number',
            headers={'Accept': 'application/json'})

        summary = browser.json['items'][0]
        self.assertEqual(
            summary,
            {
                u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-'
                        u'und-vereinbarungen/dossier-1/document-12',
                u'reference_number': u'Client1 1.1 / 1 / 12',
            })

    @browsing
    def test_summary_with_filename_on_dossiers_containing_tasks(self, browser):
        self.login(self.regular_user, browser)

        self.task.text = u'Sample description'

        browser.open(self.dossier.absolute_url() +
                     '?items.fl=filename,filesize',
                     headers={'Accept': 'application/json'})

        summary = browser.json['items'][1]
        self.assertEqual(
            {u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/'
             'vertrage-und-vereinbarungen/dossier-1/task-1',
             u'filename': None,
             u'filesize': 0}, summary)
