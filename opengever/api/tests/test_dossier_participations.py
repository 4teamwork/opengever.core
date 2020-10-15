from ftw.builder.builder import Builder
from ftw.builder.builder import create
from ftw.testbrowser import browsing
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.ogds.base.actor import ActorLookup
from opengever.testing import IntegrationTestCase
from opengever.testing import SolrIntegrationTestCase
import json
import transaction


class PloneParticipationsHelper(object):

    def add_participation(self, context, participant_id, roles, browser=None):
        handler = IParticipationAware(context)
        participation = handler.create_participation(**{"contact": participant_id, "roles": roles})
        handler.append_participiation(participation)


class SQLParticipationsHelper(object):

    def add_participation(self, context, participant_id, roles, browser):
        browser.open(context.absolute_url() + '/@participations',
                     method='POST',
                     headers=self.api_headers,
                     data=json.dumps({'participant_id': participant_id,
                                      'roles': roles}))


class TestParticipationsGet(IntegrationTestCase, PloneParticipationsHelper):

    @browsing
    def test_get_participations(self, browser):
        self.login(self.regular_user, browser=browser)
        self.add_participation(self.dossier, self.regular_user.getId(),
                               ['regard', 'participation', 'final-drawing'])
        self.add_participation(self.dossier, self.dossier_responsible.getId(), ['regard'])
        browser.open(self.dossier.absolute_url() + '/@participations',
                     method='GET', headers=self.api_headers)

        expected_json = {
            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen'
                    u'/dossier-1/@participations',
            u'available_roles': [{u'title': u'Final drawing',
                                  u'token': u'final-drawing'},
                                 {u'title': u'Participation',
                                  u'token': u'participation'},
                                 {u'title': u'Regard', u'token': u'regard'}],
            u'items': [{u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/'
                        u'vertrage-und-vereinbarungen/dossier-1/@participations/kathi.barfuss',
                        u'participant_id': u'kathi.barfuss',
                        u'participant_title': u'B\xe4rfuss K\xe4thi (kathi.barfuss)',
                        u'roles': [u'regard', u'participation', u'final-drawing']},
                       {u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/'
                        u'vertrage-und-vereinbarungen/dossier-1/@participations/robert.ziegler',
                        u'participant_id': u'robert.ziegler',
                        u'participant_title': u'Ziegler Robert (robert.ziegler)',
                        u'roles': [u'regard']}],
            u'items_total': 2}
        self.assertEqual(expected_json, browser.json)

        browser.open(self.dossier, method='GET', headers=self.api_headers)
        self.assertEqual({u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/'
                                  u'vertrage-und-vereinbarungen/dossier-1/@participations'},
                         browser.json['@components']['participations'])
        browser.open(self.dossier.absolute_url() + '?expand=participations',
                     method='GET', headers=self.api_headers)
        self.assertEqual(expected_json, browser.json['@components']['participations'])

    @browsing
    def test_response_is_batched(self, browser):
        self.login(self.regular_user, browser=browser)
        self.add_participation(self.dossier, self.regular_user.getId(),
                               ['regard', 'participation', 'final-drawing'])
        self.add_participation(self.dossier, self.dossier_responsible.getId(), ['regard'])
        browser.open(self.dossier.absolute_url() + '/@participations?b_size=1',
                     method='GET', headers=self.api_headers)

        self.assertEqual(1, len(browser.json['items']))
        self.assertEqual(2, browser.json['items_total'])
        self.assertEqual(3, len(browser.json['available_roles']))
        self.assertIn('batching', browser.json)


class TestParticipationsGetWithContactFeatureEnabled(IntegrationTestCase):

    features = ('contact', )

    @browsing
    def test_get_participations(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.dossier.absolute_url() + '/@participations',
                     method='GET', headers=self.api_headers)
        expected_json = {
            u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
                    u'dossier-1/@participations',
            u'available_roles': [{u'title': u'Final drawing',
                                  u'token': u'final-drawing'},
                                 {u'title': u'Participation',
                                  u'token': u'participation'},
                                 {u'title': u'Regard', u'token': u'regard'}],
            u'items': [{u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-'
                                u'vereinbarungen/dossier-1/@participations/organization:2',
                        u'participant_id': u'organization:2',
                        u'participant_title': u'Meier AG',
                        u'roles': [u'final-drawing']},
                       {u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/'
                                u'vertrage-und-vereinbarungen/dossier-1/@participations/person:1',
                        u'participant_id': u'person:1',
                        u'participant_title': u'B\xfchler Josef',
                        u'roles': [u'final-drawing', u'participation']}],
            u'items_total': 2}
        self.assertEqual(expected_json, browser.json)

        browser.open(self.dossier, method='GET', headers=self.api_headers)
        self.assertEqual({u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/'
                                  u'vertrage-und-vereinbarungen/dossier-1/@participations'},
                         browser.json['@components']['participations'])
        browser.open(self.dossier.absolute_url() + '?expand=participations',
                     method='GET', headers=self.api_headers)
        self.assertEqual(expected_json, browser.json['@components']['participations'])

    @browsing
    def test_response_is_batched(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier.absolute_url() + '/@participations?b_size=1',
                     method='GET', headers=self.api_headers)

        self.assertEqual(1, len(browser.json['items']))
        self.assertEqual(2, browser.json['items_total'])
        self.assertEqual(3, len(browser.json['available_roles']))
        self.assertIn('batching', browser.json)


class TestParticipationsPost(IntegrationTestCase):

    def setUp(self):
        super(TestParticipationsPost, self).setUp()
        self.valid_participant_id = self.regular_user.getId()

    @browsing
    def test_post_participation(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier.absolute_url() + '/@participations',
                     method='POST',
                     headers=self.api_headers,
                     data=json.dumps({'participant_id': self.regular_user.getId(),
                                      'roles': ['regard', 'final-drawing']}))
        self.assertEqual(browser.status_code, 204)
        contact_id = 'contact:{}'.format(self.franz_meier.getId())
        browser.open(self.dossier.absolute_url() + '/@participations',
                     method='POST',
                     headers=self.api_headers,
                     data=json.dumps({'participant_id': contact_id,
                                      'roles': ['participation']}))
        self.assertEqual(browser.status_code, 204)

        browser.open(self.dossier.absolute_url() + '/@participations', method='GET',
                     headers=self.api_headers)
        self.assertEqual([
            {u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
             u'dossier-1/@participations/kathi.barfuss',
             u'participant_id': u'kathi.barfuss',
             u'participant_title': u'B\xe4rfuss K\xe4thi (kathi.barfuss)',
             u'roles': [u'regard', u'final-drawing']},
            {u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
             u'dossier-1/@participations/contact:meier-franz',
             u'participant_id': u'contact:meier-franz',
             u'participant_title': u'Meier Franz (meier.f@example.com)',
             u'roles': [u'participation']}],
            browser.json['items'])

    @browsing
    def test_post_participations_without_roles_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        error = {"message": "A list of roles is required", "type": "BadRequest"}
        with browser.expect_http_error(400):
            browser.open(self.dossier.absolute_url() + '/@participations', method='POST',
                         headers=self.api_headers,
                         data=json.dumps({'participant_id': self.valid_participant_id}))
        self.assertEqual(error, browser.json)
        with browser.expect_http_error(400):
            browser.open(self.dossier.absolute_url() + '/@participations', method='POST',
                         headers=self.api_headers,
                         data=json.dumps({'participant_id': self.valid_participant_id,
                                          'roles': []}))
        self.assertEqual(error, browser.json)

    @browsing
    def test_post_participations_with_invalid_role_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.dossier.absolute_url() + '/@participations', method='POST',
                         headers=self.api_headers,
                         data=json.dumps({'participant_id': self.valid_participant_id,
                                          'roles': ['regard', 'invalid']}))
        self.assertEqual({"message": "Role 'invalid' does not exist",
                          "type": "BadRequest"}, browser.json)

    @browsing
    def test_post_participations_without_participant_id_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.dossier.absolute_url() + '/@participations', method='POST',
                         headers=self.api_headers,
                         data=json.dumps({'roles': ['regard']}))
        self.assertEqual({"message": "Property 'participant_id' is required",
                          "type": "BadRequest"}, browser.json)

    @browsing
    def test_post_participations_with_invalid_participant_id_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.dossier.absolute_url() + '/@participations', method='POST',
                         headers=self.api_headers,
                         data=json.dumps({'participant_id': 'chaosqueen',
                                          'roles': ['regard']}))
        self.assertEqual({"message": "chaosqueen is not a valid id",
                          "type": "BadRequest"}, browser.json)

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
        self.assertEqual({"message": "There is already a participation for {}".format(
            self.valid_participant_id), "type": "BadRequest"}, browser.json)


class TestParticipationsPostWithContactFeatureEnabled(TestParticipationsPost):

    features = ('contact', )

    def setUp(self):
        super(TestParticipationsPostWithContactFeatureEnabled, self).setUp()
        self.person = create(Builder('person').having(
            firstname=u'Hans', lastname=u'M\xfcller'))
        self.organization = create(Builder('organization').named('4teamwork AG'))
        self.org_role = create(Builder('org_role').having(
            person=self.person, organization=self.organization, function=u'Gute Fee'))
        transaction.commit()
        self.valid_participant_id = 'person:{}'.format(self.person.id)

    @browsing
    def test_post_participation(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.dossier.absolute_url() + '/@participations',
                     method='POST',
                     headers=self.api_headers,
                     data=json.dumps({'participant_id': self.valid_participant_id,
                                      'roles': ['regard']}))
        self.assertEqual(browser.status_code, 204)

        organization_id = 'organization:{}'.format(self.organization.id)
        browser.open(self.dossier.absolute_url() + '/@participations',
                     method='POST',
                     headers=self.api_headers,
                     data=json.dumps({'participant_id': organization_id,
                                      'roles': ['participation', 'final-drawing']}))
        self.assertEqual(browser.status_code, 204)

        org_role_id = 'org_role:{}'.format(self.org_role.id)
        browser.open(self.dossier.absolute_url() + '/@participations',
                     method='POST',
                     headers=self.api_headers,
                     data=json.dumps({'participant_id': org_role_id,
                                      'roles': ['regard', 'final-drawing']}))
        self.assertEqual(browser.status_code, 204)

        ogds_user_id = 'ogds_user:{}'.format(self.regular_user.getId())
        browser.open(self.dossier.absolute_url() + '/@participations',
                     method='POST',
                     headers=self.api_headers,
                     data=json.dumps({'participant_id': ogds_user_id,
                                      'roles': ['regard', 'participation', 'final-drawing']}))
        self.assertEqual(browser.status_code, 204)

        browser.open(self.dossier.absolute_url() + '/@participations', method='GET',
                     headers=self.api_headers)

        self.assertEqual([
            {u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
             u'dossier-1/@participations/organization:2',
             u'participant_id': u'organization:2',
             u'participant_title': u'Meier AG',
             u'roles': [u'final-drawing']},
            {u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
             u'dossier-1/@participations/person:1',
             u'participant_id': u'person:1',
             u'participant_title': u'B\xfchler Josef',
             u'roles': [u'final-drawing', u'participation']},
            {u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
             u'dossier-1/@participations/person:3',
             u'participant_id': self.valid_participant_id,
             u'participant_title': self.person.get_title(),
             u'roles': [u'regard']},
            {u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
             u'dossier-1/@participations/organization:4',
             u'participant_id': organization_id,
             u'participant_title': self.organization.get_title(),
             u'roles': [u'participation', u'final-drawing']},
            {u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
             u'dossier-1/@participations/org_role:1',
             u'participant_id': org_role_id,
             u'participant_title': self.org_role.get_title(),
             u'roles': [u'regard', u'final-drawing']},
            {u'@id': u'http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/'
             u'dossier-1/@participations/ogds_user:kathi.barfuss',
             u'participant_id': ogds_user_id,
             u'participant_title': u'B\xe4rfuss K\xe4thi (kathi.barfuss)',
             u'roles': [u'regard', u'participation', u'final-drawing']}],
            browser.json['items'])


class TestParticipationsPatch(IntegrationTestCase, PloneParticipationsHelper):

    def setUp(self):
        super(TestParticipationsPatch, self).setUp()
        self.participant_id = self.regular_user.getId()
        self.participant_title = ActorLookup(self.regular_user.getId()).lookup().get_label()

    @browsing
    def test_patch_participation(self, browser):
        self.login(self.regular_user, browser=browser)
        self.add_participation(self.dossier, self.participant_id, ['regard'], browser=browser)
        browser.open(self.dossier.absolute_url() + '/@participations',
                     method='GET', headers=self.api_headers)
        url = u'{}/@participations/{}'.format(self.dossier.absolute_url(), self.participant_id)
        self.assertIn({
            u'@id': url,
            u'participant_id': self.participant_id,
            u'participant_title': self.participant_title,
            u'roles': [u'regard']}, browser.json['items'])

        browser.open(self.dossier.absolute_url() + '/@participations/' + self.participant_id,
                     method='PATCH',
                     headers=self.api_headers,
                     data=json.dumps({'roles': ['participation', 'final-drawing']}))
        self.assertEqual(browser.status_code, 204)

        browser.open(self.dossier.absolute_url() + '/@participations', method='GET',
                     headers=self.api_headers)
        self.assertIn({
            u'@id': url,
            u'participant_id': self.participant_id,
            u'participant_title': self.participant_title,
            u'roles': [u'participation', u'final-drawing']}, browser.json['items'])

    @browsing
    def test_patch_participation_without_participant_id_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.dossier.absolute_url() + '/@participations',
                         method='PATCH',
                         headers=self.api_headers,
                         data=json.dumps({'roles': ['participation', 'final-drawing']}))
        self.assertEqual({"message": "Must supply participant as URL path parameter.",
                          "type": "BadRequest"}, browser.json)

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
            browser.open(self.dossier.absolute_url() + '/@participations/chaosqueen',
                         method='PATCH',
                         headers=self.api_headers,
                         data=json.dumps({'roles': ['regard']}))
        self.assertEqual({"message": "chaosqueen is not a valid id",
                          "type": "BadRequest"}, browser.json)

    @browsing
    def test_patch_participations_without_roles_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        error = {"message": "A list of roles is required", "type": "BadRequest"}
        self.add_participation(self.dossier, self.participant_id, ['regard'], browser=browser)
        url = u'{}/@participations/{}'.format(self.dossier.absolute_url(), self.participant_id)
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
        url = u'{}/@participations/{}'.format(self.dossier.absolute_url(), self.participant_id)
        with browser.expect_http_error(400):
            browser.open(url, method='PATCH', headers=self.api_headers,
                         data=json.dumps({'roles': ['regard', 'invalid']}))
        self.assertEqual({"message": "Role 'invalid' does not exist",
                          "type": "BadRequest"}, browser.json)


class TestParticipationsPatchWithContactFeatureEnabled(SQLParticipationsHelper,
                                                       TestParticipationsPatch):

    features = ('contact', )

    def setUp(self):
        super(TestParticipationsPatchWithContactFeatureEnabled, self).setUp()
        self.person = create(Builder('person').having(
            firstname=u'Hans', lastname=u'M\xfcller'))
        transaction.commit()
        self.participant_id = 'person:{}'.format(self.person.id)
        self.participant_title = self.person.get_title()


class TestParticipationsDelete(IntegrationTestCase, PloneParticipationsHelper):

    def setUp(self):
        super(TestParticipationsDelete, self).setUp()
        self.participant_id = self.regular_user.getId()
        self.participant_title = ActorLookup(self.regular_user.getId()).lookup().get_label()

    @browsing
    def test_delete_participation(self, browser):
        self.login(self.regular_user, browser=browser)
        self.add_participation(self.dossier, self.participant_id, ['regard'], browser=browser)
        browser.open(self.dossier.absolute_url() + '/@participations',
                     method='GET', headers=self.api_headers)
        self.assertIn(self.participant_id, [item['participant_id']
                                            for item in browser.json['items']])

        browser.open(self.dossier.absolute_url() + '/@participations/' + self.participant_id,
                     method='DELETE',
                     headers=self.api_headers)
        self.assertEqual(browser.status_code, 204)

        browser.open(self.dossier.absolute_url() + '/@participations', method='GET',
                     headers=self.api_headers)
        self.assertNotIn(self.participant_id, [item['participant_id']
                                               for item in browser.json['items']])

    @browsing
    def test_delete_participation_when_particpant_has_no_participation_raises_bad_request(self,
                                                                                          browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_http_error(400):
            url = self.dossier.absolute_url() + '/@participations/' + self.participant_id
            browser.open(url, method='DELETE', headers=self.api_headers)
        self.assertEqual({"message": "{} has no participations on this context".format(
            self.participant_id), "type": "BadRequest"}, browser.json)

    @browsing
    def test_delete_participations_with_invalid_participant_id_raises_bad_request(self, browser):
        self.login(self.regular_user, browser=browser)
        with browser.expect_http_error(400):
            browser.open(self.dossier.absolute_url() + '/@participations/chaosqueen',
                         method='DELETE', headers=self.api_headers)
        self.assertEqual({"message": "chaosqueen is not a valid id",
                          "type": "BadRequest"}, browser.json)


class TestParticipationsDeleteWithContactFeatureEnabled(SQLParticipationsHelper,
                                                        TestParticipationsDelete):

    features = ('contact', )

    def setUp(self):
        super(TestParticipationsDeleteWithContactFeatureEnabled, self).setUp()
        self.person = create(Builder('person').having(
            firstname=u'Hans', lastname=u'M\xfcller'))
        transaction.commit()
        self.participant_id = 'person:{}'.format(self.person.id)
        self.participant_title = self.person.get_title()


class TestPossibleParticipantsGet(SolrIntegrationTestCase):

    @browsing
    def test_get_possible_participants(self, browser):
        self.login(self.regular_user, browser=browser)
        url = self.dossier.absolute_url() + '/@possible-participants?query=fra'

        browser.open(url, method='GET', headers=self.api_headers)

        expected_json = {u'@id': url,
                         u'items': [{u'title': u'M\xfcller Fr\xe4nzi (franzi.muller)',
                                     u'token': u'franzi.muller'},
                                    {u'title': u'Meier Franz (meier.f@example.com)',
                                     u'token': u'contact:meier-franz'}],
                         u'items_total': 2}

        self.assertEqual(expected_json, browser.json)

    @browsing
    def test_response_is_batched(self, browser):
        self.login(self.regular_user, browser=browser)
        url = self.dossier.absolute_url() + '/@possible-participants?b_size=5'

        browser.open(url, method='GET', headers=self.api_headers)

        self.assertEqual(5, len(browser.json.get('items')))
        self.assertEqual(22, browser.json.get('items_total'))
        self.assertIn('batching', browser.json)


class TestPossibleParticipantsGetWithContactFeatureEnabled(SolrIntegrationTestCase):

    features = ('contact', )

    @browsing
    def test_get_possible_participants(self, browser):
        self.login(self.regular_user, browser=browser)
        url = self.dossier.absolute_url() + '/@possible-participants?query=mei'

        browser.open(url, method='GET', headers=self.api_headers)

        expected_json = {u'@id': url,
                         u'items': [{u'title': u'Meier AG',
                                     u'token': u'organization:2'},
                                    {u'title': u'Meier David (david.meier)',
                                     u'token': u'ogds_user:david.meier'}],
                         u'items_total': 2}

        self.assertEqual(expected_json, browser.json)

    @browsing
    def test_response_is_batched(self, browser):
        self.login(self.regular_user, browser=browser)
        url = self.dossier.absolute_url() + '/@possible-participants?b_size=5'

        browser.open(url, method='GET', headers=self.api_headers)
        self.assertEqual(5, len(browser.json.get('items')))
        self.assertEqual(21, browser.json.get('items_total'))
        self.assertIn('batching', browser.json)
