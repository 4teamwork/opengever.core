from opengever.base.json_response import JSONResponse
from opengever.dossier import _
from opengever.dossier.behaviors.protect_dossier import IProtectDossier
from Products.Five import BrowserView


class CheckProtectDossierConsistency(BrowserView):
    """
    """
    def __call__(self):
        json_response = JSONResponse(self.request)
        self.check_consistency(json_response)
        return json_response.dump()

    def check_consistency(self, json_response):
        if IProtectDossier(self.context).check_local_role_consistency():
            return

        json_response.warning(
            _(u'dossier_protection_inconsistency_warning',
              default="The local roles do not match with the current "
                      "dossier protection settings. If you save this "
                      "form, the local roles will be overridden."))
