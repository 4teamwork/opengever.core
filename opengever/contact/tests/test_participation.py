from ftw.builder import Builder
from ftw.builder import create
from ftw.tabbedview.interfaces import ITabbedView
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.base.oguid import Oguid
from opengever.contact.models import Participation
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.kub.interfaces import IKuBSettings
from opengever.kub.testing import KuBIntegrationTestCase
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import get_contacts_token
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


class TestParticipationsEndPoint(FunctionalTestCase):

    def setUp(self):
        super(TestParticipationsEndPoint, self).setUp()

        # adjust slice size
        api.portal.set_registry_record(
            'batch_size', 2, interface=ITabbedView)

        self.contactfolder = create(Builder('contactfolder'))
        self.meierag = create(Builder('organization').having(name=u'Meier AG'))
        self.dossier1 = create(Builder('dossier').titled(u'Dossier A'))
        self.dossier2 = create(Builder('dossier').titled(u'Dossier B'))
        self.dossier3 = create(Builder('dossier').titled(u'Dossier C'))
        create(Builder('contact_participation')
               .for_dossier(self.dossier1)
               .for_contact(self.meierag)
               .with_roles(['regard', 'final-drawing']))
        create(Builder('contact_participation')
               .for_dossier(self.dossier2)
               .for_contact(self.meierag)
               .with_roles(['participation']))
        create(Builder('contact_participation')
               .for_dossier(self.dossier3)
               .for_contact(self.meierag)
               .with_roles(['participation']))


class TestAddParticipationAction(IntegrationTestCase):

    @browsing
    def test_redirects_to_plone_implementation_add_form_when_contact_feature_is_disabled(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        factoriesmenu.add('Participant')
        self.assertEqual(
            self.dossier.absolute_url() + '/add-plone-participation', browser.url)

    @browsing
    def test_redirects_to_plone_implementation_add_form_when_contact_feature_is_enabled(self, browser):
        self.activate_feature("contact")
        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        factoriesmenu.add('Participant')
        self.assertEqual(
            self.dossier.absolute_url() + '/add-sql-participation', browser.url)

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


class TestAddForm(FunctionalTestCase):

    def setUp(self):
        super(TestAddForm, self).setUp()
        self.dossier = create(Builder('dossier'))
        self.peter = create(Builder('person')
                            .having(firstname=u'Peter', lastname=u'M\xfcller'))
        self.meier_ag = create(Builder('organization').named(u'Meier AG'))
        self.hans = create(Builder('ogds_user')
                           .id('peter')
                           .having(firstname=u'Hans', lastname=u'Peter')
                           .as_contact_adapter())

    @browsing
    def test_raises_unathorized_when_user_is_not_allowed_to_add_content(self, browser):
        self.grant('Reader')
        with browser.expect_unauthorized():
            browser.login().open(self.dossier,
                                 view='add-sql-participation')

    @browsing
    def test_add_participation_for_person(self, browser):
        browser.login().open(self.dossier, view='add-sql-participation')
        browser.fill({'Roles': ['For your information']})
        form = browser.find_form_by_field('Contact')
        form.find_widget('Contact').fill(get_contacts_token(self.peter))

        browser.click_on('Save')

        participation = Participation.query.first()
        self.assertEquals(self.peter.person_id,
                          participation.contact.person_id)
        self.assertEquals(self.dossier, participation.resolve_dossier())
        self.assertEquals(['regard'],
                          [role.role for role in participation.roles])

    @browsing
    def test_add_participation_for_ogds_user(self, browser):
        browser.login().open(self.dossier, view='add-sql-participation')
        browser.fill({'Roles': ['For your information']})
        form = browser.find_form_by_field('Contact')
        form.find_widget('Contact').fill(get_contacts_token(self.hans))

        browser.click_on('Save')

        participation = Participation.query.first()
        self.assertEquals(self.hans.id,
                          participation.ogds_user.id)
        self.assertEquals(self.dossier, participation.resolve_dossier())
        self.assertEquals(['regard'],
                          [role.role for role in participation.roles])

    @browsing
    def test_add_participation_for_organization(self, browser):
        browser.login().open(self.dossier, view='add-sql-participation')
        browser.fill({'Roles': ['Final signature', 'For your information']})
        form = browser.find_form_by_field('Contact')
        form.find_widget('Contact').fill(get_contacts_token(self.meier_ag))

        browser.click_on('Save')

        participation = Participation.query.first()
        self.assertEquals(self.meier_ag.organization_id,
                          participation.contact.organization_id)
        self.assertEquals(self.dossier, participation.resolve_dossier())
        self.assertEquals([u'final-drawing', u'regard'],
                          [role.role for role in participation.roles])

    @browsing
    def test_add_participation_for_org_role(self, browser):
        org_role = create(Builder('org_role').having(
            person=self.peter, organization=self.meier_ag, function=u'cheffe'))

        browser.login().open(self.dossier, view='add-sql-participation')
        browser.fill({'Roles': ['Final signature']})
        form = browser.find_form_by_field('Contact')
        form.find_widget('Contact').fill(get_contacts_token(org_role))

        browser.click_on('Save')

        participation = Participation.query.first()
        self.assertEqual(org_role.org_role_id,
                         participation.org_role.org_role_id)
        self.assertEquals(self.dossier, participation.resolve_dossier())
        self.assertEquals([u'final-drawing'],
                          [role.role for role in participation.roles])

    @browsing
    def test_add_already_existing_participation_raise_validation_error(self, browser):
        create(Builder('contact_participation')
               .having(contact=self.peter,
                       dossier_oguid=Oguid.for_object(self.dossier)))

        browser.login().open(self.dossier, view='add-sql-participation')

        browser.fill({'Roles': ['Final signature', 'For your information']})
        form = browser.find_form_by_field('Contact')
        form.find_widget('Contact').fill(get_contacts_token(self.peter))

        browser.click_on('Save')

        self.assertEquals(['There were some errors.'], error_messages())
        self.assertEquals(
            ['A participation already exists for this contact.'],
            browser.css('div.error').text),


class TestEditForm(FunctionalTestCase):

    def setUp(self):
        super(TestEditForm, self).setUp()
        self.contactfolder = create(Builder('contactfolder'))
        self.dossier = create(Builder('dossier'))
        self.peter = create(Builder('person')
                            .having(firstname=u'Peter', lastname=u'M\xfcller'))
        self.meier_ag = create(Builder('organization').named(u'Meier AG'))

    @browsing
    def test_edit_contact_particpation_roles(self, browser):
        participation = create(Builder('contact_participation')
                               .for_dossier(self.dossier)
                               .for_contact(self.peter))
        create(Builder('participation_role').having(
            participation=participation, role=u'regard'))
        create(Builder('participation_role').having(
            participation=participation, role=u'final-drawing'))

        browser.login().open(self.dossier,
                             view=u'tabbedview_view-participations')
        browser.click_on('Edit')

        field = browser.forms['form'].find_field('Roles')
        self.assertEquals(['Final signature', 'For your information', 'Participation'],
                          field.options)

        browser.fill({'Roles': ['Participation', 'For your information']})
        browser.click_on('Save')

        self.assertEquals(['Changes saved'], info_messages())
        self.assertEquals(
            'http://nohost/plone/dossier-1#participations', browser.url)
        self.assertItemsEqual(
            ['regard', 'participation'],
            [role.role for role in Participation.query.first().roles])

    @browsing
    def test_edit_ogs_user_participation_roles(self, browser):
        ogds_user = create(Builder('ogds_user')
                           .id('peter')
                           .having(firstname=u'Hans', lastname=u'Peter')
                           .as_contact_adapter())

        participation = create(Builder('ogds_user_participation')
                               .for_dossier(self.dossier)
                               .for_ogds_user(ogds_user))
        create(Builder('participation_role').having(
            participation=participation, role=u'final-drawing'))

        browser.login().open(self.dossier,
                             view=u'tabbedview_view-participations')
        browser.click_on('Edit')

        field = browser.forms['form'].find_field('Roles')
        self.assertEquals(['Final signature', 'For your information', 'Participation'],
                          field.options)

        browser.fill({'Roles': ['Participation', 'For your information']})
        browser.click_on('Save')

        self.assertEquals(['Changes saved'], info_messages())
        self.assertEquals(
            'http://nohost/plone/dossier-1#participations', browser.url)
        self.assertItemsEqual(
            ['participation', 'regard'],
            [role.role for role in Participation.query.first().roles])

    @browsing
    def test_edit_org_role_particpation_roles(self, browser):
        org_role = create(Builder('org_role').having(
            person=self.peter, organization=self.meier_ag, function=u'cheffe'))
        participation = create(Builder('org_role_participation')
                               .for_dossier(self.dossier)
                               .for_org_role(org_role))
        create(Builder('participation_role').having(
            participation=participation, role=u'final-drawing'))

        browser.login().open(self.dossier,
                             view=u'tabbedview_view-participations')
        browser.click_on('Edit')

        field = browser.forms['form'].find_field('Roles')
        self.assertEquals(['Final signature', 'For your information', 'Participation'],
                          field.options)

        browser.fill({'Roles': ['Participation', 'For your information']})
        browser.click_on('Save')

        self.assertEquals(['Changes saved'], info_messages())
        self.assertEquals(
            'http://nohost/plone/dossier-1#participations', browser.url)
        self.assertItemsEqual(
            ['participation', 'regard'],
            [role.role for role in Participation.query.first().roles])

    @browsing
    def test_label_contains_contact_participation_title(self, browser):
        create(Builder('contact_participation')
               .for_dossier(self.dossier)
               .for_contact(self.peter))

        browser.login().open(self.dossier,
                             view=u'tabbedview_view-participations')
        browser.click_on('Edit')

        self.assertEquals([u'Edit Participation of M\xfcller Peter'],
                          browser.css('h1').text)

    @browsing
    def test_label_contains_ogds_user_participation_title(self, browser):
        ogds_user = create(Builder('ogds_user')
                           .id('peter')
                           .having(firstname=u'Hans', lastname=u'Peter')
                           .as_contact_adapter())
        create(Builder('ogds_user_participation')
               .for_dossier(self.dossier)
               .for_ogds_user(ogds_user))

        browser.login().open(self.dossier,
                             view=u'tabbedview_view-participations')
        browser.click_on('Edit')

        self.assertEquals([u'Edit Participation of Peter Hans (peter)'],
                          browser.css('h1').text)

    @browsing
    def test_label_contains_org_role_participation_title(self, browser):
        org_role = create(Builder('org_role').having(
            person=self.peter, organization=self.meier_ag, function=u'cheffe'))
        create(Builder('org_role_participation')
               .for_dossier(self.dossier)
               .for_org_role(org_role))

        browser.login().open(self.dossier,
                             view=u'tabbedview_view-participations')
        browser.click_on('Edit')

        self.assertEquals([u'Edit Participation of M\xfcller Peter - Meier AG (cheffe)'],
                          browser.css('h1').text)

    @browsing
    def test_cancel_redirects_to_participations_tab(self, browser):
        create(Builder('contact_participation')
               .for_dossier(self.dossier)
               .for_contact(self.peter))

        browser.login().open(self.dossier,
                             view=u'tabbedview_view-participations')
        browser.click_on('Edit')

        browser.click_on('Cancel')
        self.assertEquals(
            'http://nohost/plone/dossier-1#participations', browser.url)


class TestRemoveForm(FunctionalTestCase):

    def setUp(self):
        super(TestRemoveForm, self).setUp()
        self.contactfolder = create(Builder('contactfolder'))
        self.dossier = create(Builder('dossier'))
        self.peter = create(Builder('person')
                            .having(firstname=u'Peter', lastname=u'M\xfcller'))
        self.meier_ag = create(Builder('organization').named(u'Meier AG'))

    @browsing
    def test_remove_contact_particpation(self, browser):
        participation = create(Builder('contact_participation')
                               .for_dossier(self.dossier)
                               .for_contact(self.peter))
        create(Builder('participation_role').having(
            participation=participation, role=u'regard'))

        browser.login().open(self.dossier,
                             view=u'tabbedview_view-participations')
        browser.click_on('Remove')

        browser.click_on('Remove')
        self.assertEquals(['Participation removed'], info_messages())
        self.assertEquals(
            'http://nohost/plone/dossier-1#participations', browser.url)
        self.assertEquals(0, Participation.query.count())

    @browsing
    def test_remove_ogds_user_particpation(self, browser):
        ogds_user = create(Builder('ogds_user')
                           .id('peter')
                           .having(firstname=u'Hans', lastname=u'Peter')
                           .as_contact_adapter())

        participation = create(Builder('ogds_user_participation')
                               .for_dossier(self.dossier)
                               .for_ogds_user(ogds_user))
        create(Builder('participation_role').having(
            participation=participation, role=u'final-drawing'))

        browser.login().open(self.dossier,
                             view=u'tabbedview_view-participations')
        browser.click_on('Remove')

        browser.click_on('Remove')
        self.assertEquals(['Participation removed'], info_messages())
        self.assertEquals(
            'http://nohost/plone/dossier-1#participations', browser.url)
        self.assertEquals(0, Participation.query.count())

    @browsing
    def test_remove_org_role_particpation(self, browser):
        org_role = create(Builder('org_role').having(
            person=self.peter, organization=self.meier_ag, function=u'cheffe'))
        create(Builder('org_role_participation')
               .for_dossier(self.dossier)
               .for_org_role(org_role))

        browser.login().open(self.dossier,
                             view=u'tabbedview_view-participations')
        browser.click_on('Remove')

        browser.click_on('Remove')
        self.assertEquals(['Participation removed'], info_messages())
        self.assertEquals(
            'http://nohost/plone/dossier-1#participations', browser.url)
        self.assertEquals(0, Participation.query.count())

    @browsing
    def test_label_contains_participation_contact_title(self, browser):
        create(Builder('contact_participation')
               .for_dossier(self.dossier)
               .for_contact(self.peter))

        browser.login().open(self.dossier,
                             view=u'tabbedview_view-participations')
        browser.click_on('Remove')

        self.assertEquals([u'Remove Participation of M\xfcller Peter'],
                          browser.css('h1').text)

    @browsing
    def test_cancel_redirects_to_participations_tab(self, browser):
        create(Builder('contact_participation')
               .for_dossier(self.dossier)
               .for_contact(self.peter))

        browser.login().open(self.dossier,
                             view=u'tabbedview_view-participations')
        browser.click_on('Remove')

        browser.click_on('Cancel')
        self.assertEquals(
            'http://nohost/plone/dossier-1#participations', browser.url)


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
