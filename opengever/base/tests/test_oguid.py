from ftw.builder import Builder
from ftw.builder import create
from opengever.base.oguid import Oguid
from opengever.testing import IntegrationTestCase
from unittest import TestCase
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


class TestOguidFunctional(IntegrationTestCase):

    def create_remote_au(self):
        au = create(Builder('admin_unit')
                    .id(u'remote')
                    .having(
                        site_url='http://internal/remote',
                        public_url='http://public/remote'))
        return au

    def test_oguid_for_object(self):
        self.login(self.regular_user)

        intids = getUtility(IIntIds)

        self.assertEqual('plone:{}'.format(intids.getId(self.dossier)),
                         Oguid.for_object(self.dossier))

    def test_oguid_get_url_same_admin_unit(self):
        self.login(self.regular_user)

        oguid = Oguid.for_object(self.dossier)
        self.assertEqual(self.dossier.absolute_url(), oguid.get_url())

    def test_oguid_url_different_admin_unit(self):
        self.login(self.regular_user)

        oguid = Oguid('foo', 1234)
        self.assertEqual(
            'http://nohost/plone/@@resolve_oguid?oguid=foo:1234',
            oguid.get_url())

    def test_oguid_get_remote_url_raises_if_not_remote(self):
        self.login(self.regular_user)

        oguid = Oguid.for_object(self.task)
        with self.assertRaises(Exception) as cm:
            oguid.get_remote_url()
        self.assertEqual(
            'Not a remote OGUID. Use get_url() instead', str(cm.exception))

    def test_oguid_get_remote_url_internal(self):
        self.login(self.regular_user)

        remote_au = self.create_remote_au()
        sql_task = self.task.get_sql_object()

        # Trick Oguid into thinking the task is a remote one
        sql_task.admin_unit_id = u'remote'
        oguid = Oguid.for_object(self.task)
        oguid.admin_unit_id = u'remote'

        expected_url = '/'.join((remote_au.site_url, sql_task.physical_path))
        self.assertEqual(expected_url, oguid.get_remote_url(public=False))

    def test_oguid_get_remote_url_public(self):
        self.login(self.regular_user)

        remote_au = self.create_remote_au()
        sql_task = self.task.get_sql_object()

        # Trick Oguid into thinking the task is a remote one
        sql_task.admin_unit_id = u'remote'
        oguid = Oguid.for_object(self.task)
        oguid.admin_unit_id = u'remote'

        expected_url = '/'.join((remote_au.public_url, sql_task.physical_path))
        self.assertEqual(expected_url, oguid.get_remote_url(public=True))

    def test_oguid_register_registers_intid(self):
        self.login(self.regular_user)

        copied_dossier = self.dossier._getCopy(self.leaf_repofolder)
        self.assertIsNone(Oguid.for_object(copied_dossier))

        oguid = Oguid.for_object(copied_dossier, register=True)
        self.assertIsNotNone(oguid)
        self.assertEqual(oguid, Oguid.for_object(copied_dossier))
