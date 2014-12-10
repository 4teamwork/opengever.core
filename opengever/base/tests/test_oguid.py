from ftw.builder import Builder
from ftw.builder import create
from opengever.base.oguid import Oguid
from opengever.testing import FunctionalTestCase
from unittest2 import TestCase
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class TestOguid(TestCase):

    def test_init_with_string_oguid(self):
        oguid = Oguid.parse('foo:123')
        self.assertEqual('foo', oguid.admin_unit_id)
        self.assertEqual(123, oguid.int_id)
        self.assertEqual('foo:123', oguid.id)

    def test_init_with_admin_unit_and_intid(self):
        oguid = Oguid('bar', 123)
        self.assertEqual('bar', oguid.admin_unit_id)
        self.assertEqual(123, oguid.int_id)
        self.assertEqual('bar:123', oguid.id)

    def test_oguid_string_representation(self):
        self.assertEqual('foo:123', str(Oguid.parse('foo:123')))

    def test_comparison(self):
        self.assertEqual(Oguid('foo', 2),
                         Oguid('foo', 2))
        self.assertEqual('foo:2', Oguid('foo', 2))

        self.assertNotEqual(None, Oguid('foo', 2))
        self.assertNotEqual(Oguid('foo', 3), Oguid('foo', 2))
        self.assertNotEqual(Oguid('bar', 2), Oguid('foo', 2))


class TestOguidFunctional(FunctionalTestCase):

    def test_oguid_for_object(self):
        intids = getUtility(IIntIds)

        obj = create(Builder('dossier'))
        int_id = intids.getId(obj)
        oguid = Oguid.for_object(obj)

        self.assertEqual('client1:{}'.format(int_id), oguid)
