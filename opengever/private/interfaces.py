from zope.interface import Interface


class IPrivateContainer(Interface):
    """Marker interface for private containers, only accessible
    by the corresponding user.
    """
