from zope.interface import Interface


class IRepositoryFavorites(Interface):
    """An adapter for storing repository favorites.
    The adapter used per repository root per user.
    """

    def __init__(repositoryroot, username):
        pass

    def add(uuid):
        pass

    def remove(uuid):
        pass

    def list():
        pass

    def set(uuids):
        pass
