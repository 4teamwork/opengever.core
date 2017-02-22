from ftw.builder import Builder
from ftw.builder import create
from opengever.api.testing import RelativeSession
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ZSERVER_TESTING
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD

import json
import jwt
import transaction


class TestOfficeconnectorAPI(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ZSERVER_TESTING

    def setUp(self):
        super(TestOfficeconnectorAPI, self).setUp()
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
        self.document = create(Builder('document')
                               .within(self.dossier))

        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.setDefaultLanguage('de-ch')
        lang_tool.supported_langs = ['fr-ch', 'de-ch']
        transaction.commit()

    def test_returns_404_when_feature_disabled(self):
        attach_response = self.api.get('/'
                                       'ordnungssystem/'
                                       'ordnungsposition/'
                                       'dossier-1/'
                                       'document-1/'
                                       'officeconnector_attach_url')
        self.assertEquals(404, attach_response.status_code)

        checkout_response = self.api.get('/'
                                         'ordnungssystem/'
                                         'ordnungsposition/'
                                         'dossier-1/'
                                         'document-1/'
                                         'officeconnector_checkout_url')
        self.assertEquals(404, checkout_response.status_code)

    def test_attach_to_outlook(self):
        registry_setting = {}
        registry_setting['opengever'
                         '.officeconnector'
                         '.interfaces'
                         '.IOfficeConnectorSettings'
                         '.attach_to_outlook_enabled'] = True
        self.api.patch('/@registry', json.dumps(registry_setting))
        response = self.api.get('/'
                                'ordnungssystem/'
                                'ordnungsposition/'
                                'dossier-1/'
                                'document-1/'
                                'officeconnector_attach_url')
        self.assertEquals(200, response.status_code)

        response_json = response.json()
        self.assertTrue('token' in response_json)

        token = jwt.decode(response_json['token'], verify=False)
        self.assertTrue('download' in token)
        self.assertEquals(token['action'], 'attach')
        self.assertEquals(SITE_OWNER_NAME, token['sub'])

    def test_document_checkout(self):
        registry_setting = {}
        registry_setting['opengever'
                         '.officeconnector'
                         '.interfaces'
                         '.IOfficeConnectorSettings'
                         '.direct_checkout_and_edit_enabled'] = True
        self.api.patch('/@registry', json.dumps(registry_setting))
        response = self.api.get('/'
                                'ordnungssystem/'
                                'ordnungsposition/'
                                'dossier-1/'
                                'document-1/'
                                'officeconnector_checkout_url')
        self.assertEquals(200, response.status_code)

        response_json = response.json()
        self.assertTrue('token' in response_json)

        token = jwt.decode(response_json['token'], verify=False)
        self.assertTrue('download' in token)
        self.assertEquals(token['action'], 'checkout')
        self.assertEquals(SITE_OWNER_NAME, token['sub'])
