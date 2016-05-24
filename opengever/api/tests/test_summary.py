from ftw.builder import Builder
from ftw.builder import create
from opengever.api.testing import RelativeSession
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ZSERVER_API_TESTING
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
import transaction


class TestGeverJSONSummarySerializer(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ZSERVER_API_TESTING

    def setUp(self):
        super(TestGeverJSONSummarySerializer, self).setUp()
        self.portal = self.layer['portal']

        self.api = RelativeSession(self.portal.absolute_url())
        self.api.headers.update({'Accept': 'application/json'})
        self.api.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.repo = create(Builder('repository_root')
                           .having(id='ordnungssystem',
                                   title_de=u'Ordnungssystem',
                                   title_fr=u'Syst\xe8me de classement'))
        self.repofolder = create(Builder('repository')
                                 .within(self.repo)
                                 .having(title_de=u'Ordnungsposition',
                                         title_fr=u'Position'))
        self.dossier = create(Builder('dossier')
                              .within(self.repofolder)
                              .titled(u'Mein Dossier'))

        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de-ch')
        lang_tool.supported_langs = ['fr-ch', 'de-ch']
        transaction.commit()

    def test_portal_type_is_included(self):
        response = self.api.get('/ordnungssystem')
        repofolder_summary = response.json()['items'][0]

        self.assertDictContainsSubset(
            {u'@type': u'opengever.repository.repositoryfolder'},
            repofolder_summary)

        response = self.api.get('/ordnungssystem/ordnungsposition')
        dossier_summary = response.json()['items'][0]

        self.assertDictContainsSubset(
            {u'@type': u'opengever.dossier.businesscasedossier'},
            dossier_summary)

    def test_translated_title_contained_in_summary_if_obj_translated(self):
        response = self.api.get(
            '/ordnungssystem', headers={'Accept-Language': 'de-ch'})
        repofolder_summary = response.json()['items'][0]

        self.assertDictContainsSubset(
            {u'title': u'Ordnungsposition'},
            repofolder_summary)

        response = self.api.get(
            '/ordnungssystem', headers={'Accept-Language': 'fr-ch'})
        repofolder_summary = response.json()['items'][0]

        self.assertDictContainsSubset(
            {u'title': u'Position'},
            repofolder_summary)

    def test_translated_titles_default_to_german(self):
        response = self.api.get('/ordnungssystem')
        repofolder_summary = response.json()['items'][0]

        self.assertDictContainsSubset(
            {u'title': u'Ordnungsposition'},
            repofolder_summary)

    def test_regular_title_in_summary_if_obj_not_translated(self):
        response = self.api.get('/ordnungssystem/ordnungsposition')
        dossier_summary = response.json()['items'][0]

        self.assertDictContainsSubset(
            {u'title': u'Mein Dossier'},
            dossier_summary)
