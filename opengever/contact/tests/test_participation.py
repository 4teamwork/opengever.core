from ftw.builder import Builder
from ftw.builder import create
from opengever.base.oguid import Oguid
from opengever.testing import FunctionalTestCase
from opengever.testing import MEMORY_DB_LAYER
import unittest2


class TestParticipation(unittest2.TestCase):

    layer = MEMORY_DB_LAYER

    def test_adding(self):
        contact = create(Builder('person').having(
            firstname=u'peter', lastname=u'hans'))
        participation = create(Builder('participation').having(
            contact=contact,
            dossier_oguid=Oguid('foo', 1234)))

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
