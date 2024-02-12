from opengever.dossiertransfer import is_dossier_transfer_feature_enabled
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest


class DossierTransfersBase(Service):
    """Base service class for all @dossier-transfer endpoints.
    """

    def render(self):
        if not is_dossier_transfer_feature_enabled():
            raise BadRequest("Feature 'dossier_transfers' is not enabled.")
        return super(DossierTransfersBase, self).render()

    def serialize(self, transfer):
        return getMultiAdapter((transfer, getRequest()), ISerializeToJson)()
