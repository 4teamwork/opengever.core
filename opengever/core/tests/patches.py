import inspect
from Products.CMFQuickInstallerTool import events


def disable_quickinstaller_snapshots():
    """Patches Products.CMFQuickInstallerTool:
    Removes the quickinstaller's subscribers to GenericSetup events
    which create snapshots for each installed profile.

    The snapshots are used for uninstalling products, which is ususally
    not done in tests.

    Creating the snapshots consume quite a lot of time.
    Disabling it speeds up the testing layer setup time.

    We do an early monkey patch so that the event registration still works
    and the Plone fixture also profits from the patch.
    It is a marmoset patch so that we don't have to cope with function pointers.
    """

    marmoset_patch(events.handleBeforeProfileImportEvent,
                   noop_event_handler)

    marmoset_patch(events.handleProfileImportedEvent,
                   noop_event_handler)


def noop_event_handler(event):
    """An event handler that does nothing.
    """


def marmoset_patch(old, new, extra_globals={}):
    print 'PATCH {}: replace {}.{} with {}'.format(
        marmoset_patch.__module__,
        old.__module__, old.__name__,
        new.__name__)

    g = old.func_globals
    g.update(extra_globals)
    c = inspect.getsource(new)
    exec c in g

    old.func_code = g[new.__name__].func_code
