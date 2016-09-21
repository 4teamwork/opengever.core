from opengever.dossier.base import DossierContainer
from opengever.dossier.businesscase import IBusinessCaseDossier


class IPrivateDossier(IBusinessCaseDossier, IPrivateContainer):
    """PrivateDossier marker interface.
    """


class PrivateDossier(DossierContainer):
    """A specific dossier type, only addable to a PrivateFolder in the
    private Area and only visible for the Owner and Managers.
    """
