from opengever.globalindex.oguid import Oguid
from unittest2 import TestCase


class TestOguid(TestCase):

    def test_init_fails_with_too_few_parameters(self):
        with self.assertRaises(AssertionError):
            Oguid()

    def test_init_fails_with_too_many_parameters(self):
        with self.assertRaises(AssertionError):
            Oguid(id='foo:123', admin_unit_id='mah', intid=3)

    def test_init_with_string_oguid(self):
        oguid = Oguid(id='foo:123')
        self.assertEqual('foo', oguid.admin_unit_id)
        self.assertEqual(123, oguid.intid)
        self.assertEqual('foo:123', oguid.id)

    def test_init_with_oguid(self):
        oguid = Oguid(Oguid('foo:123'))
        self.assertEqual('foo', oguid.admin_unit_id)
        self.assertEqual(123, oguid.intid)
        self.assertEqual('foo:123', oguid.id)

    def test_init_with_admin_unit_and_intid(self):
        oguid = Oguid(admin_unit_id='bar', intid='123')
        self.assertEqual('bar', oguid.admin_unit_id)
        self.assertEqual(123, oguid.intid)
        self.assertEqual('bar:123', oguid.id)

    def test_oguid_string_representation(self):
        oguid = Oguid(id='foo:123')
        self.assertEqual('foo:123', str(oguid))
