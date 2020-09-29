from plone import api
from ZODB.DemoStorage import DemoStorage


ABSENT_MARKER = object()


class ZODBStorageInReadonlyMode(object):
    """Context manager that allows to temporarily set the DemoStorage used in
    tests to read-only mode, and restore the mode to the original state
    afterwards.

    This currently only works for FunctionalTests unfortunately, but not
    IntegrationTests.

    Simulating a True return value from 'isReadOnly' may work in
    IntegrationTests, but attempts to commit the transaction will raise a
    POSException.ReadOnlyError, which will mess with the IntegrationTestCase's
    transaction simulation (using savepoints).

    Testing the behavior in readonly mode on txn.commit() in an
    IntegrationTest is sort of a moot point anyway, since exactly that aspect
    is faked, and any such test therefore would give little assurances about
    real world behavior.
    """

    def __init__(self):
        portal = api.portal.get()
        self._storage = portal._p_jar.db().storage
        assert isinstance(self._storage, DemoStorage)

    def __enter__(self):
        self.backup()
        self.set_read_only()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.restore()

    def backup(self):
        self._orig_is_read_only = getattr(self._storage, '_is_read_only', ABSENT_MARKER)

    def set_read_only(self):
        """Enable readonly mode for the current DemoStorage.

        This will set the '_is_read_only' flag on that DS. All the work needed
        to actualy *respect* that flag is done by the patches in
        og.testing.patch.patch_demostorage_to_support_readonly_mode.

        That flag keeps track of the actual internal state in ClientStorage.
        It doesn't normally exist on DemoStorage, and will be removed again
        when leaving the context manager.

        This takes care of the current DemoStorage instance. But since
        Plone stacks several DemoStorages in order to achieve inexpensive
        isolation, new DS instances may be spawned and chained.

        Since this happens during layer setup, the lifetime ouf our
        context manager should never spawn a timeframe where a new DS
        is instantiated using stackDemoStorage(). If it turns out that it
        does, patching DemoStorage.__init__ here to also set newly created
        ones to read-only, and self-register themselves in a tracking list
        attached to this context manager, to then clean them up on restore,
        would be one way to address this.
        """
        setattr(self._storage, '_is_read_only', True)

    def restore(self):
        if self._orig_is_read_only is ABSENT_MARKER:
            delattr(self._storage, '_is_read_only')
        else:
            setattr(self._storage, '_is_read_only', self._orig_is_read_only)
