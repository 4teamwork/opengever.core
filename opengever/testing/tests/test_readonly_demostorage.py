from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.testing import FunctionalTestCase
from opengever.testing.readonly import ZODBStorageInReadonlyMode
from persistent.list import PersistentList
from Products.CMFPlone.utils import safe_hasattr
from unittest import expectedFailure
from ZODB import POSException
import transaction


class TestDemoStorageReadOnlySupport(FunctionalTestCase):

    def setUp(self):
        super(TestDemoStorageReadOnlySupport, self).setUp()
        self.portal.existing_obj = PersistentList()

    def test_storage_correctly_reports_readonly_mode_if_disabled(self):
        conn = self.portal._p_jar
        storage = conn.db().storage
        self.assertFalse(storage.isReadOnly())

    def test_storage_correctly_reports_readonly_mode_if_enabled(self):
        with ZODBStorageInReadonlyMode():
            conn = self.portal._p_jar
            storage = conn.db().storage
            self.assertTrue(storage.isReadOnly())

    def test_connection_correctly_reports_readonly_mode_if_disabled(self):
        conn = self.portal._p_jar
        self.assertFalse(conn.isReadOnly())

    def test_connection_correctly_reports_readonly_mode_if_enabled(self):
        with ZODBStorageInReadonlyMode():
            conn = self.portal._p_jar
            self.assertTrue(conn.isReadOnly())

    def test_raises_read_only_error_on_obj_creation(self):
        with ZODBStorageInReadonlyMode():
            self.portal.new_obj = PersistentList()
            with self.assertRaises(POSException.ReadOnlyError):
                transaction.commit()

        self.assertFalse(safe_hasattr(self.portal, 'new_obj'))

    def test_raises_read_only_error_on_obj_mutation(self):
        with ZODBStorageInReadonlyMode():
            self.portal.title = u'Changed title'
            with self.assertRaises(POSException.ReadOnlyError):
                transaction.commit()

        self.assertEqual(u'Plone site', self.portal.title)

    def test_raises_read_only_error_on_obj_deletion(self):
        self.grant('Manager')
        with ZODBStorageInReadonlyMode():
            del self.portal.existing_obj
            with self.assertRaises(POSException.ReadOnlyError):
                transaction.commit()

        self.assertTrue(safe_hasattr(self.portal, 'existing_obj'))

    def test_context_manager_resets_mode_on_exit(self):
        with ZODBStorageInReadonlyMode():
            pass

        conn = self.portal._p_jar
        storage = conn.db().storage

        self.assertFalse(getattr(storage, '_is_read_only', False))
        self.assertFalse(conn.isReadOnly())
        self.assertFalse(storage.isReadOnly())

    def test_context_manager_removes_flag_on_exit(self):
        with ZODBStorageInReadonlyMode():
            pass

        conn = self.portal._p_jar
        storage = conn.db().storage

        self.assertFalse(hasattr(storage, '_is_read_only'))

    def test_context_manager_can_be_nested_without_issues(self):
        conn = self.portal._p_jar
        storage = conn.db().storage

        self.assertFalse(hasattr(storage, '_is_read_only'))

        with ZODBStorageInReadonlyMode():
            with ZODBStorageInReadonlyMode():
                self.assertTrue(getattr(storage, '_is_read_only', False))

            self.assertTrue(getattr(storage, '_is_read_only', False))

        self.assertFalse(hasattr(storage, '_is_read_only'))


class TestDemoStorageReadOnlySupportTestbrowser(FunctionalTestCase):

    def setUp(self):
        super(TestDemoStorageReadOnlySupportTestbrowser, self).setUp()
        self.dossier = create(Builder('dossier'))
        self.document = create(Builder('document'))

    @browsing
    def test_readonly_mode_stays_enabled_after_testbrowser_requests(self, browser):
        browser.login()

        self.assertFalse(self.portal._p_jar.isReadOnly())
        with ZODBStorageInReadonlyMode():
            self.assertTrue(self.portal._p_jar.isReadOnly())
            browser.open(self.portal)
            conn = self.portal._p_jar
            self.assertTrue(conn.isReadOnly())

    @expectedFailure
    @browsing
    def test_raises_read_only_error_on_content_creation(self, browser):
        """This test currently fails because we now withdraw the Contributor
        role from users in ReadOnly mode. We therefore never even get to the
        ReadOnlyError being raised.
        """
        browser.login().open(self.portal)

        browser.exception_bubbling = True
        with ZODBStorageInReadonlyMode():
            factoriesmenu.add('Document')
            with self.assertRaises(POSException.ReadOnlyError):
                browser.fill({'Title': u'Foo'}).save()

        self.assertEqual(0, len(self.dossier.objectValues()))

    @browsing
    def test_raises_read_only_error_on_content_modification(self, browser):
        self.grant('Editor')
        browser.login().open(self.document)
        browser.open(self.document, view='edit')

        browser.exception_bubbling = True
        with ZODBStorageInReadonlyMode():
            with self.assertRaises(POSException.ReadOnlyError):
                browser.fill({'Title': 'Foo', }).save()

        self.assertEqual(u'Testdokum\xe4nt', self.document.title)
