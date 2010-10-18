from zope.interface import Interface


class IRestrictedDossier(Interface):
    """A restricted dossier is not addable by default in the repository folder.

    In each repository folder object it's possible to allow a restricted
    dossier in the editform of the repository folder.
    """
