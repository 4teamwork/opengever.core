from ftw.builder import Builder
from ftw.builder import create
from opengever.base.oguid import Oguid
from opengever.testing import MEMORY_DB_LAYER
import unittest


class TestContactParticipation(unittest.TestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestContactParticipation, self).setUp()
        self.contact = create(Builder('person').having(
            firstname=u'peter', lastname=u'hans'))

    def test_adding(self):
        create(Builder('contact_participation')
               .having(contact=self.contact, dossier_oguid=Oguid('foo', 1234)))

    def test_copy_participation(self):
        participation = create(Builder('contact_participation').having(
            contact=self.contact,
            dossier_oguid=Oguid('foo', 1234)))
        create(Builder('participation_role')
               .having(participation=participation, role=u'Sch\xf6ff'))

        copied_participation = participation.copy()
        self.assertEqual(self.contact, copied_participation.contact)
        self.assertEqual('foo', copied_participation.dossier_admin_unit_id)
        self.assertEqual(1234, copied_participation.dossier_int_id)
        self.assertEqual(1, len(copied_participation.roles))
        copied_role = copied_participation.roles[0]
        self.assertEqual(u'Sch\xf6ff', copied_role.role)

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


class TestOgdsUserParticipation(unittest.TestCase):

    layer = MEMORY_DB_LAYER

    def test_adding(self):
        peter = create(Builder('ogds_user').id('peter').as_contact_adapter())
        create(Builder('ogds_user_participation').having(
            ogds_user=peter,
            dossier_oguid=Oguid('foo', 1234)))

    def test_copy_participation(self):
        peter = create(Builder('ogds_user').id('peter').as_contact_adapter())
        participation = create(Builder('ogds_user_participation').having(
            ogds_user=peter,
            dossier_oguid=Oguid('foo', 1234)))

        copied_participation = participation.copy()
        self.assertEqual(peter, copied_participation.ogds_user)
        self.assertEqual('foo', copied_participation.dossier_admin_unit_id)
        self.assertEqual(1234, copied_participation.dossier_int_id)
        self.assertEqual(0, len(copied_participation.roles))


class TestOrgRoleParticipation(unittest.TestCase):

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

    def test_copy_participation(self):
        person = create(Builder('person').having(
            firstname=u'peter', lastname=u'hans'))
        organization = create(Builder('organization').named('ACME'))
        orgrole = create(Builder('org_role').having(
            person=person, organization=organization, function=u'cheffe'))
        participation = create(Builder('org_role_participation').having(
            org_role=orgrole,
            dossier_oguid=Oguid('foo', 1234)))

        copied_participation = participation.copy()
        self.assertEqual(orgrole, copied_participation.org_role)
        self.assertEqual('foo', copied_participation.dossier_admin_unit_id)
        self.assertEqual(1234, copied_participation.dossier_int_id)
        self.assertEqual(0, len(copied_participation.roles))
