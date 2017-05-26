from plone.directives import form
from opengever.dossier.base import DossierContainer



class IContracDossierSchema(form.Schema):
    """Empty schema - contract specific fields are added via behavior.
    """


class ContractDossier(DossierContainer):
    """A contract dossier
    """
