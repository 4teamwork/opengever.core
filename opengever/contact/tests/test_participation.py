from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from opengever.base.oguid import Oguid
from opengever.contact.models.participation import Participation
from opengever.testing import FunctionalTestCase
from opengever.testing import MEMORY_DB_LAYER
from zExceptions import Unauthorized
import unittest2


class TestParticipation(unittest2.TestCase):

    layer = MEMORY_DB_LAYER

    def test_adding(self):
        contact = create(Builder('person').having(
            firstname=u'peter', lastname=u'hans'))
        create(Builder('participation')
               .having(contact=contact, dossier_oguid=Oguid('foo', 1234)))

    def test_participation_can_have_multiple_roles(self):
        contact = create(Builder('person').having(
            firstname=u'peter', lastname=u'hans'))
        participation = create(Builder('participation').having(
            contact=contact,
            dossier_oguid=Oguid('foo', 1234)))
        role1 = create(Builder('participation_role').having(
            participation=participation,
            role=u'Sch\xf6ff'))
        role2 = create(Builder('participation_role').having(
            participation=participation,
            role=u'Hanswutscht'))

        self.assertEquals([role1, role2], participation.roles)


class TestDossierParticipation(FunctionalTestCase):

    def test_relation_to_dossier(self):
        dossier = create(Builder('dossier'))
        contact = create(Builder('person').having(
            firstname=u'peter', lastname=u'hans'))
        participation = create(Builder('participation').having(
            contact=contact,
            dossier_oguid=Oguid.for_object(dossier)))

        self.assertEqual(dossier, participation.resolve_dossier())


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
                                 view='add-contact-participation')

    @browsing
    def test_add_participation_for_person(self, browser):
        browser.login().open(self.dossier, view='add-contact-participation')
        browser.fill({'Contact': str(self.peter.contact_id),
                      'Roles': ['Regard']})
        browser.click_on('Add')

        participation = Participation.query.first()
        self.assertEquals(self.peter.person_id,
                          participation.contact.person_id)
        self.assertEquals(self.dossier, participation.resolve_dossier())
        self.assertEquals(['regard'],
                          [role.role for role in participation.roles])

    @browsing
    def test_add_participation_for_organization(self, browser):
        browser.login().open(self.dossier, view='add-contact-participation')
        browser.fill({'Contact': str(self.meier_ag.contact_id),
                      'Roles': ['Final drawing', 'Regard']})
        browser.click_on('Add')

        participation = Participation.query.first()
        self.assertEquals(self.meier_ag.organization_id,
                          participation.contact.organization_id)
        self.assertEquals(self.dossier, participation.resolve_dossier())
        self.assertEquals([u'final-drawing', u'regard'],
                          [role.role for role in participation.roles])

    @browsing
    def test_add_already_existing_participation_raise_validation_error(self, browser):
        create(Builder('participation')
               .having(contact=self.peter,
                       dossier_oguid=Oguid.for_object(self.dossier)))

        browser.login().open(self.dossier, view='add-contact-participation')
        browser.fill({'Contact': str(self.peter.contact_id),
                      'Roles': ['Final drawing', 'Regard']})
        browser.click_on('Add')

        self.assertEquals(['There were some errors.'], error_messages())
        self.assertEquals(
            ['There already exists a participation for this contact.'],
            browser.css('div.error').text),
