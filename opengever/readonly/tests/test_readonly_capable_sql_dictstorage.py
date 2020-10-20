from ftw.dictstorage.interfaces import IConfig
from ftw.dictstorage.interfaces import IDictStorage
from ftw.dictstorage.sql import DictStorageModel
from opengever.base.model import create_session
from opengever.readonly.dictstorage import ReadOnlyCapableSQLDictStorage
from opengever.testing import IntegrationTestCase
from opengever.testing.readonly import ZODBStorageInReadonlyMode
from zope.component import getMultiAdapter
from zope.component import queryAdapter


class TestReadOnlyCapableSQLDictStorage(IntegrationTestCase):

    def get_dictstorage(self, context):
        config = queryAdapter(context, IConfig)
        storage = getMultiAdapter((context, config), IDictStorage)
        return storage

    def test_readonly_capable_sql_dictstorage_is_used(self):
        self.login(self.regular_user)

        tabbed_view = self.dossier.restrictedTraverse('tabbed_view')
        storage = self.get_dictstorage(tabbed_view)
        self.assertIsInstance(storage, ReadOnlyCapableSQLDictStorage)

    def test_regular_storage_still_works_in_rw_mode(self):
        self.login(self.regular_user)

        tabbed_view = self.dossier.restrictedTraverse('tabbed_view')
        storage = self.get_dictstorage(tabbed_view)
        storage['foo'] = 'bar'

        session = create_session()
        self.assertEqual(1, session.query(DictStorageModel).count())
        record = session.query(DictStorageModel).one()
        self.assertEqual('foo', record.key)
        self.assertEqual('bar', record.value)

    def test_readonly_capable_sql_dictstorage_doesnt_write_in_ro_mode(self):
        self.login(self.regular_user)

        with ZODBStorageInReadonlyMode():
            tabbed_view = self.dossier.restrictedTraverse('tabbed_view')
            storage = self.get_dictstorage(tabbed_view)
            storage['foo'] = 'bar'

        session = create_session()
        self.assertEqual(0, session.query(DictStorageModel).count())
