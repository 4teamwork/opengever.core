from opengever.globalindex.oguid import Oguid
from unittest2 import TestCase


class TestOguid(TestCase):

    def test_init_fails_with_too_few_parameters(self):
        with self.assertRaises(AssertionError):
            Oguid()

    def test_init_fails_with_too_many_parameters(self):
        with self.assertRaises(AssertionError):
            Oguid(id='foo:123', admin_unit_id='mah', int_id=3)

    def test_init_with_string_oguid(self):
        oguid = Oguid(id='foo:123')
        self.assertEqual('foo', oguid.admin_unit_id)
        self.assertEqual(123, oguid.int_id)
        self.assertEqual('foo:123', oguid.id)

    def test_init_with_oguid(self):
        oguid = Oguid(id=Oguid(id='foo:123'))
        self.assertEqual('foo', oguid.admin_unit_id)
        self.assertEqual(123, oguid.int_id)
        self.assertEqual('foo:123', oguid.id)

    def test_init_with_admin_unit_and_intid(self):
        oguid = Oguid(admin_unit_id='bar', int_id='123')
        self.assertEqual('bar', oguid.admin_unit_id)
        self.assertEqual(123, oguid.int_id)
        self.assertEqual('bar:123', oguid.id)

    def test_oguid_string_representation(self):
        oguid = Oguid(id='foo:123')
        self.assertEqual('foo:123', str(oguid))
