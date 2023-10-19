from ftw.testbrowser import browsing
from opengever.contact.tests import create_contacts
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.dossier.interfaces import IDossierParticipants
from opengever.dossier.participations import IParticipationData
from opengever.kub.testing import KuBIntegrationTestCase
from opengever.ogds.base.actor import ActorLookup
from opengever.testing import IntegrationTestCase
from opengever.testing import SolrIntegrationTestCase
from plone import api
import json
import requests_mock


class TestParticipationsGet(IntegrationTestCase):

    @browsing
    def test_get_participations(self, browser):
        self.login(self.regular_user, browser=browser)
        handler = IParticipationAware(self.dossier)
        handler.add_participation(self.regular_user.getId(),
                                  ['regard', 'participation', 'final-drawing'])
        handler.add_participation(self.dossier_responsible.getId(), ['regard'])
        browser.open(self.dossier.absolute_url() + '/@participations',
                     method='GET', headers=self.api_headers)

        expected_json = {
            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen'
                    u'/dossier-1/@participations',
            u'available_roles': [{u'title': u'Final signature',
                                  u'token': u'final-drawing',
                                  u'active': True},
                                 {u'title': u'For your information',
                                  u'token': u'regard',
                                  u'active': True},
                                 {u'title': u'Participation',
                                  u'token': u'participation',
                                  u'active': True},
                                 ],
            u'items': [{u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/'
                        u'vertrage-und-vereinbarungen/dossier-1/@participations/regular_user',
                        u'participant_id': u'kathi.barfuss',
                        u'participant_title': u'B\xe4rfuss K\xe4thi (kathi.barfuss)',
                        u'participant_actor': {
                            u'@id': u'http://nohost/plone/@actors/regular_user',
                            u'identifier': u'kathi.barfuss'},
                        u'roles': [u'regard', u'participation', u'final-drawing']},
                       {u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/'
                        u'vertrage-und-vereinbarungen/dossier-1/@participations/dossier_responsible',
                        u'participant_id': u'robert.ziegler',
                        u'participant_title': u'Ziegler Robert (robert.ziegler)',
                        u'participant_actor': {
                            u'@id': u'http://nohost/plone/@actors/dossier_responsible',
                            u'identifier': u'robert.ziegler'},
                        u'roles': [u'regard']}],
            u'items_total': 2,
            u'primary_participation_roles': []}
        self.assertEqual(expected_json, browser.json)

        browser.open(self.dossier, method='GET', headers=self.api_headers)
        self.assertEqual({u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/'
                                  u'vertrage-und-vereinbarungen/dossier-1/@participations'},
                         browser.json['@components']['participations'])
        browser.open(self.dossier.absolute_url() + '?expand=participations',
                     method='GET', headers=self.api_headers)
        self.assertEqual(expected_json, browser.json['@components']['participations'])

    @browsing
    def test_get_participations_returns_primary_participation_roles(self, browser):
        self.login(self.regular_user, browser=browser)
        api.portal.set_registry_record(
            name='primary_participation_roles', interface=IDossierParticipants,
            value=['regard', 'final-drawing'])
        browser.open(self.dossier, view='@participations', method='GET', headers=self.api_headers)

        self.assertEqual([{u'title': u'For your information', u'token': u'regard'},
                          {u'title': u'Final signature', u'token': u'final-drawing'}],
                         browser.json['primary_participation_roles'])

    @browsing
    def test_response_is_batched(self, browser):
        self.login(self.regular_user, browser=browser)
        handler = IParticipationAware(self.dossier)
        handler.add_participation(self.regular_user.getId(),
                                  ['regard', 'participation', 'final-drawing'])
        handler.add_participation(self.dossier_responsible.getId(),
                                  ['regard'])

        browser.open(self.dossier.absolute_url() + '/@participations?b_size=1',
                     method='GET', headers=self.api_headers)

        self.assertEqual(1, len(browser.json['items']))
        self.assertEqual(2, browser.json['items_total'])
        self.assertEqual(3, len(browser.json['available_roles']))
        self.assertIn('batching', browser.json)

    @browsing
    def test_available_roles_can_be_deactivated_through_the_registry(self, browser):
        self.login(self.regular_user, browser=browser)
        api.portal.set_registry_record(
            name='roles', interface=IDossierParticipants,
            value=['regard', 'final-drawing'])
        browser.open(self.dossier, view='@participations', method='GET', headers=self.api_headers)

        self.assertEqual(
            [
                {
                    u'title': u'Final signature',
                    u'token': u'final-drawing',
                    u'active': True
                },
                {
                    u'title': u'For your information',
                    u'token': u'regard',
                    u'active': True
                },
                {
                    u'title': u'Participation',
                    u'token': u'participation',
                    u'active': False
                },
            ],
            browser.json['available_roles']
        )


@requests_mock.Mocker()
class TestParticipationsGetWithKubFeatureEnabled(KuBIntegrationTestCase):

    @browsing
    def test_get_participations(self, mocker, browser):
        self.login(self.regular_user, browser=browser)
        handler = IParticipationAware(self.dossier)

        self.mock_labels(mocker)
        handler.add_participation(
            self.person_jean, ['regard', 'participation', 'final-drawing'])
        handler.add_participation(self.org_ftw, ['regard'])
        handler.add_participation(self.memb_jean_ftw, ['participation'])

        participations_url = "{}/@participations".format(self.dossier.absolute_url())

        expected_json = {
            u'@id': participations_url,
            u'available_roles': [{u'title': u'Final signature',
                                  u'token': u'final-drawing',
                                  u'active': True},
                                 {u'title': u'For your information',
                                  u'token': u'regard',
                                  u'active': True},
                                 {u'title': u'Participation',
                                  u'token': u'participation',
                                  u'active': True}],
            u'items': [
                {u'@id': "{}/{}".format(participations_url, self.org_ftw),
                 u'participant_actor': {
                    u'@id': u'http://nohost/plone/@actors/' + self.org_ftw,
                    u'identifier': self.org_ftw},
                 u'participant_id': self.org_ftw,
                 u'participant_title': u'4Teamwork',
                 u'roles': [u'regard']},
                {u'@id': "{}/{}".format(participations_url, self.person_jean),
                 u'participant_actor': {
                    u'@id': u'http://nohost/plone/@actors/' + self.person_jean,
                    u'identifier': self.person_jean},
                 u'participant_id': self.person_jean,
                 u'participant_title': u'Dupont Jean',
                 u'roles': [u'regard', u'participation', u'final-drawing']},
                {u'@id': "{}/{}".format(participations_url, self.memb_jean_ftw),
                 u'participant_actor': {
                    u'@id': u'http://nohost/plone/@actors/' + self.memb_jean_ftw,
                    u'identifier': self.memb_jean_ftw},
                 u'participant_id': self.memb_jean_ftw,
                 u'participant_title': u'Dupont Jean - 4Teamwork (CEO)',
                 u'roles': [u'participation']},
            ],
            u'items_total': 3,
            u'primary_participation_roles': []}

        browser.open(self.dossier.absolute_url() + '/@participations',
                     method='GET', headers=self.api_headers)

        self.assertEqual(expected_json, browser.json)

        browser.open(self.dossier, method='GET', headers=self.api_headers)
        self.assertEqual({u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/'
                                  u'vertrage-und-vereinbarungen/dossier-1/@participations'},
                         browser.json['@components']['participations'])
        browser.open(self.dossier.absolute_url() + '?expand=participations',
                     method='GET', headers=self.api_headers)
        self.assertEqual(expected_json, browser.json['@components']['participations'])

    @browsing
    def test_response_is_batched(self, mocker, browser):
        self.login(self.regular_user, browser=browser)
        handler = IParticipationAware(self.dossier)

        self.mock_labels(mocker)
        handler.add_participation(
            self.person_jean, ['regard', 'participation', 'final-drawing'])

        handler.add_participation(self.org_ftw, ['regard'])

        browser.open(self.dossier.absolute_url() + '/@participations?b_size=1',
                     method='GET', headers=self.api_headers)

        self.assertEqual(1, len(browser.json['items']))
        self.assertEqual(2, browser.json['items_total'])
        self.assertEqual(3, len(browser.json['available_roles']))
        self.assertIn('batching', browser.json)

    @browsing
    def test_participants_are_sorted_by_title(self, mocker, browser):
        self.login(self.regular_user, browser=browser)
        handler = IParticipationAware(self.dossier)

        self.mock_labels(mocker)
        handler.add_participation(self.person_jean, ['regard'])
        handler.add_participation(self.person_julie, ['participation'])
        handler.add_participation(self.regular_user.getId(), ['participation'])
        handler.add_participation(self.dossier_responsible.getId(), ['regard'])

        browser.open(self.dossier, view='@participations',
                     method='GET', headers=self.api_headers)
        self.assertEqual([u'B\xe4rfuss K\xe4thi (kathi.barfuss)', u'Dupont Jean', u'Dupont Julie',
                          u'Ziegler Robert (robert.ziegler)'], [item['participant_title']
                         for item in browser.json['items']])


class ParticipationsPostTestMixin():

    @browsing
    def test_post_participation(self, browser):
        self.login(self.regular_user, browser=browser)
        handler = IParticipationAware(self.empty_dossier)

        self.assertEqual(0, len(list(handler.get_participations())))
        self.assertFalse(handler.has_participation(self.valid_participant_id))
        self.assertFalse(handler.has_participation(self.valid_participant_id2))

        browser.open(self.empty_dossier.absolute_url() + '/@participations',
                     method='POST',
                     headers=self.api_headers,
                     data=json.dumps({'participant_id': self.valid_participant_id,
                                      'roles': ['regard', 'final-drawing']}))
        self.assertEqual(browser.status_code, 204)

        self.assertEqual(1, len(list(handler.get_participations())))
        self.assertTrue(handler.has_participation(self.valid_participant_id))

        browser.open(self.empty_dossier.absolute_url() + '/@participations',
                     method='POST',
                     headers=self.api_headers,
                     data=json.dumps({'participant_id': self.valid_participant_id2,
                                      'roles': ['participation']}))
        self.assertEqual(browser.status_code, 204)
        self.assertEqual(2, len(list(handler.get_participations())))
        self.assertTrue(handler.has_participation(self.valid_participant_id2))

        participations = [IParticipationData(participation)
                          for participation in handler.get_participations()]
        self.assertItemsEqual(
            [self.valid_participant_id, self.valid_participant_id2],
            [data.participant_id for data in participations])
        self.assertItemsEqual(
            [['regard', 'final-drawing'], ['participation']],
            [data.roles for data in participations])

    @browsing
    def test_post_participations_without_roles_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        error = {"message": "A list of roles is required", "type": "BadRequest"}

        with browser.expect_http_error(400):
            browser.open(self.dossier.absolute_url() + '/@participations',
                         method='POST',
                         headers=self.api_headers,
                         data=json.dumps({'participant_id': self.valid_participant_id}))
        self.assertEqual(error, browser.json)

        with browser.expect_http_error(400):
            browser.open(self.dossier.absolute_url() + '/@participations',
                         method='POST',
                         headers=self.api_headers,
                         data=json.dumps({'participant_id': self.valid_participant_id,
                                          'roles': []}))
        self.assertEqual(error, browser.json)

    @browsing
    def test_post_participations_with_invalid_role_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.dossier.absolute_url() + '/@participations',
                         method='POST',
                         headers=self.api_headers,
                         data=json.dumps({'participant_id': self.valid_participant_id,
                                          'roles': ['regard', 'invalid']}))
        self.assertEqual({"message": "Role 'invalid' does not exist",
                          "type": "BadRequest"}, browser.json)

    @browsing
    def test_post_participations_without_participant_id_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.dossier.absolute_url() + '/@participations',
                         method='POST',
                         headers=self.api_headers,
                         data=json.dumps({'roles': ['regard']}))
        self.assertEqual({"message": "Property 'participant_id' is required",
                          "type": "BadRequest"}, browser.json)

    @browsing
    def test_post_participations_with_invalid_participant_id_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.dossier.absolute_url() + '/@participations',
                         method='POST',
                         headers=self.api_headers,
                         data=json.dumps({'participant_id': 'invalid-id',
                                          'roles': ['regard']}))
        self.assertEqual({"message": "invalid-id is not a valid id",
                          "type": "BadRequest"},
                         browser.json)

    @browsing
    def test_post_participation_with_existing_participant_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier.absolute_url() + '/@participations',
                     method='POST',
                     headers=self.api_headers,
                     data=json.dumps({'participant_id': self.valid_participant_id,
                                      'roles': ['regard']}))
        with browser.expect_http_error(400):
            browser.open(self.dossier.absolute_url() + '/@participations',
                         method='POST',
                         headers=self.api_headers,
                         data=json.dumps({'participant_id': self.valid_participant_id,
                                          'roles': ['final-drawing']}))
        self.assertEqual(
            {"message": "There is already a participation for {}".format(
             self.valid_participant_id),
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_post_participation_for_resolved_dossier_raises_unauthorized(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(401):
            browser.open(self.expired_dossier, view='/@participations',
                         method='POST',
                         headers=self.api_headers,
                         data=json.dumps({'participant_id': self.valid_participant_id,
                                          'roles': ['regard']}))
        self.assertEqual({"message": "You are not authorized to access this resource.",
                          "type": "Unauthorized"}, browser.json)

    @browsing
    def test_post_participation_for_inactive_dossier_raises_unauthorized(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(401):
            browser.open(self.inactive_dossier, view='/@participations',
                         method='POST',
                         headers=self.api_headers,
                         data=json.dumps({'participant_id': self.valid_participant_id,
                                          'roles': ['regard']}))
        self.assertEqual({"message": "You are not authorized to access this resource.",
                          "type": "Unauthorized"}, browser.json)


class TestParticipationsPost(IntegrationTestCase, ParticipationsPostTestMixin):

    def setUp(self):
        super(TestParticipationsPost, self).setUp()
        create_contacts(self)
        self.valid_participant_id = self.regular_user.getId()
        with self.login(self.regular_user):
            self.valid_participant_id2 = 'contact:{}'.format(self.franz_meier.getId())


@requests_mock.Mocker()
class TestParticipationsPostWithKubFeatureEnabled(KuBIntegrationTestCase, ParticipationsPostTestMixin):

    def setUp(self):
        super(TestParticipationsPostWithKubFeatureEnabled, self).setUp()
        self.valid_participant_id = self.person_jean
        self.valid_participant_id2 = self.org_ftw

    def test_post_participation(self, mocker):
        self.mock_labels(mocker)
        self.mock_get_by_id(mocker, self.valid_participant_id)
        self.mock_get_by_id(mocker, self.valid_participant_id2)
        super(TestParticipationsPostWithKubFeatureEnabled, self).test_post_participation()

    def test_post_participations_without_roles_raises_bad_request(self, mocker):
        self.mock_labels(mocker)
        self.mock_get_by_id(mocker, self.valid_participant_id)
        super(TestParticipationsPostWithKubFeatureEnabled, self).test_post_participations_without_roles_raises_bad_request()

    def test_post_participations_with_invalid_role_raises_bad_request(self, mocker):
        self.mock_labels(mocker)
        self.mock_get_by_id(mocker, self.valid_participant_id)
        super(TestParticipationsPostWithKubFeatureEnabled, self).test_post_participations_with_invalid_role_raises_bad_request()

    def test_post_participations_without_participant_id_raises_bad_request(self, mocker):
        super(TestParticipationsPostWithKubFeatureEnabled, self).test_post_participations_without_participant_id_raises_bad_request()

    def test_post_participations_with_invalid_participant_id_raises_bad_request(self, mocker):
        self.mock_get_by_id(mocker, 'invalid-id')
        super(TestParticipationsPostWithKubFeatureEnabled, self).test_post_participations_with_invalid_participant_id_raises_bad_request()

    def test_post_participation_with_existing_participant_raises_bad_request(self, mocker):
        self.mock_labels(mocker)
        self.mock_get_by_id(mocker, self.valid_participant_id)
        super(TestParticipationsPostWithKubFeatureEnabled, self).test_post_participation_with_existing_participant_raises_bad_request()

    def test_post_participation_for_resolved_dossier_raises_unauthorized(self, mocker):
        self.mock_get_by_id(mocker, self.valid_participant_id)
        super(TestParticipationsPostWithKubFeatureEnabled, self).test_post_participation_for_resolved_dossier_raises_unauthorized()

    def test_post_participation_for_inactive_dossier_raises_unauthorized(self, mocker):
        self.mock_get_by_id(mocker, self.valid_participant_id)
        super(TestParticipationsPostWithKubFeatureEnabled, self).test_post_participation_for_inactive_dossier_raises_unauthorized()


class TestParticipationsPatch(IntegrationTestCase):

    def setUp(self):
        super(TestParticipationsPatch, self).setUp()
        self.participant_id = self.regular_user.getId()
        self.participant_title = ActorLookup(
            self.regular_user.getId()).lookup().get_label()

    @browsing
    def test_patch_participation(self, browser):
        self.login(self.regular_user, browser=browser)
        handler = IParticipationAware(self.dossier)
        handler.add_participation(self.participant_id, ['regard'])

        participation = handler.get_participation(self.participant_id)
        self.assertItemsEqual(
            [u'regard'], IParticipationData(participation).roles)

        browser.open(
            self.dossier.absolute_url() + '/@participations/' + self.participant_id,
            method='PATCH',
            headers=self.api_headers,
            data=json.dumps({'roles': ['participation', 'final-drawing']}))
        self.assertEqual(browser.status_code, 204)

        participation = handler.get_participation(self.participant_id)
        self.assertItemsEqual(
            [u'participation', u'final-drawing'],
            IParticipationData(participation).roles)

    @browsing
    def test_patch_participation_without_participant_id_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.dossier.absolute_url() + '/@participations',
                         method='PATCH',
                         headers=self.api_headers,
                         data=json.dumps({'roles': ['participation', 'final-drawing']}))
        self.assertEqual(
            {"message": "Must supply participant as URL path parameter.",
             "type": "BadRequest"},
            browser.json)

    @browsing
    def test_patch_participation_when_particpant_has_no_participation_raises_bad_request(self,
                                                                                         browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_http_error(400):
            url = self.dossier.absolute_url() + '/@participations/' + self.participant_id
            browser.open(url, method='PATCH', headers=self.api_headers,
                         data=json.dumps({'roles': ['participation', 'final-drawing']}))
        self.assertEqual({"message": "{} has no participations on this context".format(
            self.participant_id), "type": "BadRequest"}, browser.json)

    @browsing
    def test_patch_participations_with_invalid_participant_id_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.dossier.absolute_url() + '/@participations/invalid-id',
                         method='PATCH',
                         headers=self.api_headers,
                         data=json.dumps({'roles': ['regard']}))
        self.assertEqual({"message": "invalid-id is not a valid id",
                          "type": "BadRequest"}, browser.json)

    @browsing
    def test_patch_participations_without_roles_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        error = {"message": "A list of roles is required", "type": "BadRequest"}
        handler = IParticipationAware(self.dossier)
        handler.add_participation(self.participant_id, ['regard'])
        url = u'{}/@participations/{}'.format(
            self.dossier.absolute_url(), self.participant_id)

        with browser.expect_http_error(400):
            browser.open(url, method='PATCH', headers=self.api_headers)
        self.assertEqual(error, browser.json)

        with browser.expect_http_error(400):
            browser.open(url, method='PATCH', headers=self.api_headers,
                         data=json.dumps({'roles': []}))
        self.assertEqual(error, browser.json)

    @browsing
    def test_patch_participations_with_invalid_role_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        url = u'{}/@participations/{}'.format(
            self.dossier.absolute_url(), self.participant_id)
        handler = IParticipationAware(self.dossier)
        handler.add_participation(self.participant_id, ['regard'])
        with browser.expect_http_error(400):
            browser.open(url, method='PATCH', headers=self.api_headers,
                         data=json.dumps({'roles': ['regard', 'invalid']}))
        self.assertEqual({"message": "Role 'invalid' does not exist",
                          "type": "BadRequest"}, browser.json)

    @browsing
    def test_patch_participation_for_resolved_dossier_raises_unauthorized(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(401):
            browser.open(self.expired_dossier, view='/@participations',
                         method='PATCH',
                         headers=self.api_headers,
                         data=json.dumps({'roles': ['participation', 'final-drawing']}))

        self.assertEqual({"message": "You are not authorized to access this resource.",
                          "type": "Unauthorized"}, browser.json)

    @browsing
    def test_patch_participation_for_inactive_dossier_raises_unauthorized(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(401):
            browser.open(self.inactive_dossier, view='/@participations',
                         method='PATCH',
                         headers=self.api_headers,
                         data=json.dumps({'roles': ['participation', 'final-drawing']}))

        self.assertEqual({"message": "You are not authorized to access this resource.",
                          "type": "Unauthorized"}, browser.json)


@requests_mock.Mocker()
class TestParticipationsPatchWithKuBFeatureEnabled(KuBIntegrationTestCase, TestParticipationsPatch):

    def setUp(self):
        super(TestParticipationsPatchWithKuBFeatureEnabled, self).setUp()
        self.participant_id = self.person_jean

    def test_patch_participation(self, mocker):
        self.mock_labels(mocker)
        self.mock_get_by_id(mocker, self.participant_id)
        super(TestParticipationsPatchWithKuBFeatureEnabled, self).test_patch_participation()

    def test_patch_participation_without_participant_id_raises_bad_request(self, mocker):
        self.mock_labels(mocker)
        super(TestParticipationsPatchWithKuBFeatureEnabled, self).test_patch_participation_without_participant_id_raises_bad_request()

    def test_patch_participation_when_particpant_has_no_participation_raises_bad_request(self,
                                                                                         mocker):
        self.mock_get_by_id(mocker, self.participant_id)
        self.mock_labels(mocker)
        super(TestParticipationsPatchWithKuBFeatureEnabled, self).test_patch_participation_when_particpant_has_no_participation_raises_bad_request()

    def test_patch_participations_with_invalid_participant_id_raises_bad_request(self, mocker):
        self.mock_get_by_id(mocker, "invalid-id")
        self.mock_labels(mocker)
        super(TestParticipationsPatchWithKuBFeatureEnabled, self).test_patch_participations_with_invalid_participant_id_raises_bad_request()

    def test_patch_participations_without_roles_raises_bad_request(self, mocker):
        self.mock_get_by_id(mocker, self.participant_id)
        self.mock_labels(mocker)
        super(TestParticipationsPatchWithKuBFeatureEnabled, self).test_patch_participations_without_roles_raises_bad_request()

    def test_patch_participations_with_invalid_role_raises_bad_request(self, mocker):
        self.mock_labels(mocker)
        self.mock_get_by_id(mocker, self.participant_id)
        super(TestParticipationsPatchWithKuBFeatureEnabled, self).test_patch_participations_with_invalid_role_raises_bad_request()

    def test_patch_participation_for_resolved_dossier_raises_unauthorized(self, mocker):
        self.mock_labels(mocker)
        super(TestParticipationsPatchWithKuBFeatureEnabled, self).test_patch_participation_for_resolved_dossier_raises_unauthorized()

    def test_patch_participation_for_inactive_dossier_raises_unauthorized(self, mocker):
        self.mock_labels(mocker)
        super(TestParticipationsPatchWithKuBFeatureEnabled, self).test_patch_participation_for_inactive_dossier_raises_unauthorized()


class TestParticipationsDelete(IntegrationTestCase):

    def setUp(self):
        super(TestParticipationsDelete, self).setUp()
        self.participant_id = self.regular_user.getId()
        self.participant_title = ActorLookup(self.regular_user.getId()).lookup().get_label()

    @browsing
    def test_delete_participation(self, browser):
        self.login(self.regular_user, browser=browser)
        handler = IParticipationAware(self.dossier)
        handler.add_participation(self.participant_id, ['regard'])

        self.assertTrue(handler.has_participation(self.participant_id))

        browser.open(
            self.dossier.absolute_url() + '/@participations/' + self.participant_id,
            method='DELETE',
            headers=self.api_headers)
        self.assertEqual(browser.status_code, 204)
        self.assertFalse(handler.has_participation(self.participant_id))

    @browsing
    def test_delete_participation_when_participant_has_no_participation_raises_bad_request(
            self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_http_error(400):
            url = self.dossier.absolute_url() + '/@participations/' + self.participant_id
            browser.open(url, method='DELETE', headers=self.api_headers)
        self.assertEqual({"message": "{} has no participations on this context".format(
            self.participant_id), "type": "BadRequest"}, browser.json)

    @browsing
    def test_can_delete_participations_with_invalid_participant_id(self, browser):
        self.login(self.regular_user, browser=browser)
        invalid_id = 'invalid-id'
        handler = IParticipationAware(self.dossier)
        participation = handler.create_participation(invalid_id, ['regard'])
        handler.append_participation(participation)
        self.dossier.reindexObject(idxs=["participations", "UID"])
        self.assertTrue(handler.has_participation(invalid_id))

        browser.open(self.dossier.absolute_url() + '/@participations/' + invalid_id,
                     method='DELETE', headers=self.api_headers)
        self.assertEqual(browser.status_code, 204)
        self.assertFalse(handler.has_participation(invalid_id))

    @browsing
    def test_delete_participation_for_resolved_dossier_raises_unauthorized(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(401):
            browser.open(self.expired_dossier,
                         view='/@participations/' + self.participant_id,
                         method='DELETE', headers=self.api_headers)

        self.assertEqual({"message": "You are not authorized to access this resource.",
                          "type": "Unauthorized"}, browser.json)

    @browsing
    def test_delete_participation_for_inactive_dossier_raises_unauthorized(self, browser):
        self.login(self.regular_user, browser=browser)

        with browser.expect_http_error(401):
            browser.open(self.inactive_dossier,
                         view='/@participations/' + self.participant_id,
                         method='DELETE', headers=self.api_headers)

        self.assertEqual({"message": "You are not authorized to access this resource.",
                          "type": "Unauthorized"}, browser.json)


@requests_mock.Mocker()
class TestParticipationsDeleteWithKuBFeatureEnabled(KuBIntegrationTestCase, TestParticipationsDelete):

    def setUp(self):
        super(TestParticipationsDeleteWithKuBFeatureEnabled, self).setUp()
        self.participant_id = self.person_jean

    def test_delete_participation(self, mocker):
        self.mock_get_by_id(mocker, self.participant_id)
        self.mock_labels(mocker)
        super(TestParticipationsDeleteWithKuBFeatureEnabled, self).test_delete_participation()

    def test_delete_participation_when_participant_has_no_participation_raises_bad_request(
            self, mocker):
        self.mock_get_by_id(mocker, self.participant_id)
        self.mock_labels(mocker)
        super(TestParticipationsDeleteWithKuBFeatureEnabled, self).test_delete_participation_when_participant_has_no_participation_raises_bad_request()

    def test_can_delete_participations_with_invalid_participant_id(self, mocker):
        self.mock_get_by_id(mocker, "invalid-id")
        self.mock_labels(mocker)
        super(TestParticipationsDeleteWithKuBFeatureEnabled, self).test_can_delete_participations_with_invalid_participant_id()

    def test_delete_participation_for_resolved_dossier_raises_unauthorized(self, mocker):
        super(TestParticipationsDeleteWithKuBFeatureEnabled, self).test_delete_participation_for_resolved_dossier_raises_unauthorized()

    def test_delete_participation_for_inactive_dossier_raises_unauthorized(self, mocker):
        super(TestParticipationsDeleteWithKuBFeatureEnabled, self).test_delete_participation_for_inactive_dossier_raises_unauthorized()


class TestPossibleParticipantsGet(SolrIntegrationTestCase):

    @browsing
    def test_get_possible_participants_filters_out_current_participants(self, browser):
        self.login(self.regular_user, browser=browser)
        url = self.dossier.absolute_url() + '/@possible-participants?query=fra'

        browser.open(url, method='GET', headers=self.api_headers)

        expected_json = {u'@id': url,
                         u'items': [{u'title': u'M\xfcller Fr\xe4nzi (franzi.muller)',
                                     u'token': u'franzi.muller'}],
                         u'items_total': 1}

        self.assertEqual(expected_json, browser.json)

        handler = IParticipationAware(self.dossier)
        handler.add_participation('franzi.muller', ['regard'])

        browser.open(url, method='GET', headers=self.api_headers)

        expected_json = {u'@id': url,
                         u'items': [],
                         u'items_total': 0}

        self.assertEqual(expected_json, browser.json)

    @browsing
    def test_response_is_batched(self, browser):
        self.login(self.regular_user, browser=browser)
        url = self.dossier.absolute_url() + '/@possible-participants?b_size=5'

        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(5, len(browser.json.get('items')))
        self.assertEqual(22, browser.json.get('items_total'))
        self.assertIn('batching', browser.json)


class TestParticipationsExpansion(IntegrationTestCase):

    @browsing
    def test_participation_expansion_on_dossier(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.empty_dossier, headers=self.api_headers)
        self.assertIn(u'participations', browser.json['@components'])
        url = "{}/@participations".format(self.empty_dossier.absolute_url())
        self.assertEqual(
            {'@id': url},
            browser.json['@components']['participations'])

        handler = IParticipationAware(self.empty_dossier)
        participation = handler.add_participation(self.regular_user.id, ['regard'])
        data = IParticipationData(participation)
        browser.open(
            self.empty_dossier.absolute_url() + '?expand=participations',
            method='GET',
            headers=self.api_headers)

        expected = {
            u'@id': url,
            u'available_roles': [{u'title': u'Final signature',
                                  u'token': u'final-drawing',
                                  u'active': True},
                                 {u'title': u'For your information',
                                  u'token': u'regard',
                                  u'active': True},
                                 {u'title': u'Participation',
                                  u'token': u'participation',
                                  u'active': True},
                                 ],
            u'items': [{u'@id': '{}/{}'.format(url, data.participant_id),
                        u'participant_id': data.participant_id,
                        u'participant_title': data.participant_title,
                        u'participant_actor': {
                            u'@id': u'http://nohost/plone/@actors/' + data.participant_id,
                            u'identifier': data.participant_id},
                        u'roles': data.roles}],
            u'items_total': 1,
            u'primary_participation_roles': [],
        }
        self.assertEqual(expected, browser.json['@components']['participations'])

    @browsing
    def test_participation_expansion_is_not_available_on_private_dossiers(self, browser):
        self.login(self.regular_user, browser=browser)
        self.assertFalse(IParticipationAware.providedBy(self.private_dossier))
        browser.open(self.private_dossier, headers=self.api_headers)
        self.assertNotIn(u'participations', browser.json['@components'])
