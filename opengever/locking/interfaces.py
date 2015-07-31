from zope.interface import Interface


class ISQLLockable(Interface):
    """Marker interface for lockable sql objects or wrapper(objects)."""
