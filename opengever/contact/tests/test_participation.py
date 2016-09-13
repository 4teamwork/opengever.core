from ftw.builder import Builder
from ftw.builder import create
from ftw.tabbedview.interfaces import ITabbedView
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.base.oguid import Oguid
from opengever.contact.interfaces import IContactSettings
from opengever.contact.models.participation import Participation
from opengever.core.testing import toggle_feature
from opengever.testing import FunctionalTestCase
from opengever.testing import MEMORY_DB_LAYER
from opengever.testing.helpers import get_contacts_vocabulary
from plone import api
from zExceptions import Unauthorized
import unittest2


def get_token(obj):
    return get_contacts_vocabulary().getTerm(obj).token


class TestContactParticipation(unittest2.TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestContactParticipation, self).setUp()
        self.contact = create(Builder('person').having(
            firstname=u'peter', lastname=u'hans'))

    def test_adding(self):
        create(Builder('contact_participation')
               .having(contact=self.contact, dossier_oguid=Oguid('foo', 1234)))

    def test_participation_can_have_multiple_roles(self):
        participation = create(Builder('contact_participation').having(
            contact=self.contact,
            dossier_oguid=Oguid('foo', 1234)))
        role1 = create(Builder('participation_role').having(
            participation=participation,
            role=u'Sch\xf6ff'))
        role2 = create(Builder('participation_role').having(
            participation=participation,
            role=u'Hanswutscht'))

        self.assertEquals([role1, role2], participation.roles)

    def test_update_roles_removes_existing_no_longer_used_roles(self):
        participation = create(Builder('contact_participation').having(
            contact=self.contact,
            dossier_oguid=Oguid('foo', 1234)))
        create(Builder('participation_role').having(
            participation=participation,
            role=u'final-drawing'))
        create(Builder('participation_role').having(
            participation=participation,
            role=u'regard'))

        participation.update_roles(['regard'])
        self.assertEquals(['regard'],
                          [role.role for role in participation.roles])

    def test_update_roles_add_new_roles(self):
        contact = create(Builder('person').having(
            firstname=u'peter', lastname=u'hans'))
        participation = create(Builder('contact_participation').having(
            contact=contact,
            dossier_oguid=Oguid('foo', 1234)))
        create(Builder('participation_role').having(
            participation=participation,
            role=u'final-drawing'))
        create(Builder('participation_role').having(
            participation=participation,
            role=u'regard'))

        participation.update_roles(['regard', 'participation'])

        self.assertEquals(['regard', 'participation'],
                          [role.role for role in participation.roles])


class TestOrgRoleParticipation(unittest2.TestCase):

    layer = MEMORY_DB_LAYER

    def test_adding(self):
        person = create(Builder('person').having(
            firstname=u'peter', lastname=u'hans'))
        organization = create(Builder('organization').named('ACME'))
        orgrole = create(Builder('org_role').having(
            person=person, organization=organization, function=u'cheffe'))

        create(Builder('org_role_participation').having(
            org_role=orgrole,
            dossier_oguid=Oguid('foo', 1234)))

    def test_participation_can_have_multiple_roles(self):
        person = create(Builder('person').having(
            firstname=u'peter', lastname=u'hans'))
        organization = create(Builder('organization').named('ACME'))
        orgrole = create(Builder('org_role').having(
            person=person, organization=organization, function=u'cheffe'))

        participation = create(Builder('org_role_participation').having(
            org_role=orgrole,
            dossier_oguid=Oguid('foo', 1234)))

        role1 = create(Builder('participation_role').having(
            participation=participation,
            role=u'Sch\xf6ff'))
        role2 = create(Builder('participation_role').having(
            participation=participation,
            role=u'Hanswutscht'))

        self.assertEquals([role1, role2], participation.roles)


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


class TestParticipationWrapper(FunctionalTestCase):

    def setUp(self):
        super(TestParticipationWrapper, self).setUp()
        self.dossier = create(Builder('dossier'))
        self.hans = create(Builder('person')
                           .having(firstname=u'Hans', lastname=u'M\xfcller'))
        self.participation = create(Builder('contact_participation')
                                    .for_dossier(self.dossier)
                                    .for_contact(self.hans))

    @browsing
    def test_dossier_participation_endpoint(self, browser):
        browser.login().open('{}/participation-1/edit'.format(
            self.dossier.absolute_url()))

        self.assertEqual(
            [u'Edit Participation of Hans M\xfcller'],
            browser.css('h1').text)
        self.assertEqual(
            [u'You are here: Client1 / dossier-1 / Participation of Hans M\xfcller'],
            browser.css('#portal-breadcrumbs').text)

    @browsing
    def test_cross_injection_raises_unauthorized(self, browser):
        dossier2 = create(Builder('dossier'))
        with self.assertRaises(Unauthorized):
            browser.login().open('{}/participation-1/edit'.format(
                dossier2.absolute_url()))


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

    @browsing
    def test_returns_a_list_of_serialized_participations_the_latest_first(self, browser):
        browser.login().open(self.meierag.get_url('participations/list'))

        self.assertEqual(
            [{u'roles': [{u'label': u'Participation'}],
              u'title': u'Dossier C',
              u'url': u'http://nohost/plone/dossier-3'},
             {u'roles': [{u'label': u'Participation'}],
              u'title': u'Dossier B',
              u'url': u'http://nohost/plone/dossier-2'}],
            browser.json.get('participations'))

    @browsing
    def test_include_org_role_participations_for_the_current_context(self, browser):
        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))
        role1 = create(Builder('org_role')
                       .having(person=peter, organization=self.meierag))
        create(Builder('org_role_participation')
               .for_dossier(self.dossier2)
               .with_roles(['regard'])
               .for_org_role(role1))

        teamwork = create(Builder('organization').named('4teamwork AG'))
        role2 = create(Builder('org_role')
                       .having(person=peter, organization=teamwork))
        create(Builder('org_role_participation')
               .for_dossier(self.dossier1)
               .with_roles(['regard'])
               .for_org_role(role2))

        # organization
        browser.login().open(self.meierag.get_url('participations/list'),
                             {'show_all': 'true'})
        self.assertEqual(
            [u'Dossier B', u'Dossier C', u'Dossier B', u'Dossier A'],
            [item.get('title') for item in browser.json.get('participations')])

        # person
        browser.login().open(peter.get_url('participations/list'),
                             {'show_all': 'true'})
        self.assertEqual(
            [u'Dossier A', u'Dossier B'],
            [item.get('title') for item in browser.json.get('participations')])

    @browsing
    def test_is_sliced_and_has_more_flag_is_set_when_slice_size_is_exceeded(self, browser):
        browser.login().open(self.meierag.get_url('participations/list'))

        self.assertEqual(browser.json.get('has_more'), True)
        self.assertEqual(
            [u'Dossier C', u'Dossier B'],
            [participation.get('title') for participation
             in browser.json.get('participations')])

    @browsing
    def test_show_all_link(self, browser):
        browser.login().open(self.meierag.get_url('participations/list'))

        self.assertEqual(u'Show all 3 participations',
                         browser.json.get('show_all_label'))

    @browsing
    def test_returns_all_participations_when_request_flag_is_set(self, browser):
        browser.login().open(self.meierag.get_url('participations/list'),
                             {'show_all': 'true'})

        self.assertEqual(
            [u'Dossier C', u'Dossier B', u'Dossier A'],
            [participation.get('title') for participation
             in browser.json.get('participations')])


class TestAddParticipationAction(FunctionalTestCase):

    def setUp(self):
        super(TestAddParticipationAction, self).setUp()
        self.dossier = create(Builder('dossier'))

    @browsing
    def test_redirects_to_plone_implementation_add_form_when_contact_feature_is_disabled(self, browser):
        toggle_feature(IContactSettings, enabled=False)
        browser.login().open(self.dossier)
        factoriesmenu.add('Participant')
        self.assertEqual(
            'http://nohost/plone/dossier-1/add-plone-participation', browser.url)

    @browsing
    def test_redirects_to_plone_implementation_add_form_when_contact_feature_is_enabled(self, browser):
        toggle_feature(IContactSettings, enabled=True)
        browser.login().open(self.dossier)
        factoriesmenu.add('Participant')
        self.assertEqual(
            'http://nohost/plone/dossier-1/add-sql-participation', browser.url)


class TestAddForm(FunctionalTestCase):

    def setUp(self):
        super(TestAddForm, self).setUp()
        self.dossier = create(Builder('dossier'))
        self.peter = create(Builder('person')
                            .having(firstname=u'Peter', lastname=u'M\xfcller'))
        self.meier_ag = create(Builder('organization').named(u'Meier AG'))

    @browsing
    def test_raises_unathorized_when_user_is_not_allowed_to_add_content(self, browser):
        self.grant('Reader')
        with self.assertRaises(Unauthorized):
            browser.login().open(self.dossier,
                                 view='add-sql-participation')

    @browsing
    def test_add_participation_for_person(self, browser):
        browser.login().open(self.dossier, view='add-sql-participation')
        browser.fill({'Contact': get_token(self.peter),
                      'Roles': ['Regard']})
        browser.click_on('Save')

        participation = Participation.query.first()
        self.assertEquals(self.peter.person_id,
                          participation.contact.person_id)
        self.assertEquals(self.dossier, participation.resolve_dossier())
        self.assertEquals(['regard'],
                          [role.role for role in participation.roles])

    @browsing
    def test_add_participation_for_organization(self, browser):
        browser.login().open(self.dossier, view='add-sql-participation')
        browser.fill({'Contact': get_token(self.meier_ag),
                      'Roles': ['Final drawing', 'Regard']})
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
        browser.fill({'Contact': get_token(org_role),
                      'Roles': ['Final drawing']})
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

        browser.fill({'Contact': get_token(self.peter),
                      'Roles': ['Final drawing', 'Regard']})
        browser.click_on('Save')

        self.assertEquals(['There were some errors.'], error_messages())
        self.assertEquals(
            ['There already exists a participation for this contact.'],
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
        self.assertEquals(['Final drawing', 'Participation', 'Regard'],
                          field.options)

        browser.fill({'Roles': ['Participation', 'Regard']})
        browser.click_on('Save')

        self.assertEquals(['Changes saved'], info_messages())
        self.assertEquals(
            'http://nohost/plone/dossier-1#participations', browser.url)
        self.assertItemsEqual(
            ['regard', 'participation'],
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
        self.assertEquals(['Final drawing', 'Participation', 'Regard'],
                          field.options)

        browser.fill({'Roles': ['Participation', 'Regard']})
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

        self.assertEquals([u'Edit Participation of Peter M\xfcller'],
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

        self.assertEquals([u'Edit Participation of Peter M\xfcller - Meier AG (cheffe)'],
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

        self.assertEquals([u'Remove Participation of Peter M\xfcller'],
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
