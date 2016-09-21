from ftw.builder import Builder
from ftw.builder import create
from opengever.base.oguid import Oguid
from opengever.contact.ogdsuser import OgdsUserAdapter
from opengever.testing import MEMORY_DB_LAYER
import unittest2


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


class TestOgdsUserParticipation(unittest2.TestCase):

    layer = MEMORY_DB_LAYER

    def test_adding(self):
        adapted_peter = OgdsUserAdapter(
            create(Builder('ogds_user').id('peter')))

        create(Builder('ogds_user_participation').having(
            ogds_user=adapted_peter,
            dossier_oguid=Oguid('foo', 1234)))


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
