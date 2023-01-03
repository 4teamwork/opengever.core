from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import error_messages
from opengever.base.oguid import Oguid
from opengever.contact.models import Participation
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.kub.interfaces import IKuBSettings
from opengever.kub.testing import KuBIntegrationTestCase
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from plone import api
from requests_toolbelt.utils import formdata
import requests_mock


class TestDossierParticipation(FunctionalTestCase):

    def test_contact_relation_to_dossier(self):
        dossier = create(Builder('dossier'))
        contact = create(Builder('person').having(
            firstname=u'peter', lastname=u'hans'))
        participation = create(Builder('contact_participation').having(
            contact=contact,
            dossier_oguid=Oguid.for_object(dossier)))

        self.assertEqual(dossier, participation.resolve_dossier())

    def test_org_role_relation_to_dossier(self):
        dossier = create(Builder('dossier'))
        peter = create(Builder('person').having(
            firstname=u'peter', lastname=u'hans'))
        organization = create(Builder('organization').named('ACME'))
        org_role = create(Builder('org_role').having(
            person=peter, organization=organization, function=u'cheffe'))

        participation = create(Builder('org_role_participation').having(
            org_role=org_role,
            dossier_oguid=Oguid.for_object(dossier)))

        self.assertEqual(dossier, participation.resolve_dossier())

    def test_ogds_user_relation_to_dossier(self):
        dossier = create(Builder('dossier'))
        ogds_user = create(Builder('ogds_user')
                           .id('peter')
                           .having(firstname=u'Hans', lastname=u'Peter')
                           .as_contact_adapter())

        participation = create(Builder('ogds_user_participation')
                               .for_dossier(dossier)
                               .for_ogds_user(ogds_user))

        self.assertEqual(dossier, participation.resolve_dossier())

    def test_participations_are_copied_when_dossier_is_copied(self):
        dossier = create(Builder('dossier'))
        peter = create(Builder('person').having(
            firstname=u'peter', lastname=u'hans'))
        organization = create(Builder('organization').named('ACME'))
        org_role = create(Builder('org_role').having(
            person=peter, organization=organization, function=u'cheffe'))
        ogds_user = create(Builder('ogds_user')
                           .id('peter')
                           .having(firstname=u'Hans', lastname=u'Peter')
                           .as_contact_adapter())
        create(Builder('ogds_user_participation')
               .for_dossier(dossier)
               .for_ogds_user(ogds_user))
        create(Builder('contact_participation')
               .having(contact=peter, dossier_oguid=Oguid.for_object(dossier)))
        create(Builder('contact_participation')
               .having(contact=organization,
                       dossier_oguid=Oguid.for_object(dossier)))
        create(Builder('org_role_participation')
               .having(org_role=org_role,
                       dossier_oguid=Oguid.for_object(dossier)))

        original_participations = Participation.query.by_dossier(dossier).all()

        copied_dossier = api.content.copy(source=dossier, target=self.portal)
        copied_participations = Participation.query.by_dossier(copied_dossier).all()
        self.assertEqual(4, len(copied_participations))
        intersecting_elements = set(original_participations).intersection(
                                                    set(copied_participations))
        self.assertEqual(0, len(intersecting_elements))


class TestAddParticipationAction(IntegrationTestCase):

    @browsing
    def test_redirects_to_plone_implementation_add_form_when_contact_feature_is_disabled(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        factoriesmenu.add('Participant')
        self.assertEqual(
            self.dossier.absolute_url() + '/add-plone-participation', browser.url)

    @browsing
    def test_redirects_to_folder_with_error_message_when_kub_feature_is_enabled(self, browser):
        api.portal.set_registry_record(
            'base_url', u'http://localhost:8000', IKuBSettings)
        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        factoriesmenu.add('Participant')
        self.assertEqual(
            ['The Contact and Authorities directory is only supported in the new UI.'],
            error_messages())
        self.assertEqual(self.dossier.absolute_url(), browser.url)


@requests_mock.Mocker()
class TestRemoveKubParticipation(KuBIntegrationTestCase):

    @browsing
    def test_deleting_kub_participation_is_not_supported(self, mocker, browser):
        self.login(self.regular_user, browser)
        self.mock_labels(mocker)
        self.mock_get_by_id(mocker, self.person_jean)
        handler = IParticipationAware(self.empty_dossier)
        handler.add_participation(self.person_jean, roles=['participation'])

        original_template = (
            'orig_template',
            '#'.join((self.empty_dossier.absolute_url(), 'participants')))
        oids = ('oids', self.person_jean)
        method = ('delete_participants:method', '1')
        browser.open(
            self.empty_dossier.absolute_url(),
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data=formdata.urlencode((original_template, oids, method, )),
            )

        self.assertEqual(
            ['The Contact and Authorities directory is only supported in the new UI.'],
            error_messages())
        self.assertEqual(
            [self.person_jean],
            [part.contact for part in handler.get_participations()])
