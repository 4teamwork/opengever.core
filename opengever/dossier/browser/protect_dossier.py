from opengever.dossier import _
from opengever.dossier.behaviors.protect_dossier import IProtectDossier
from Products.Five import BrowserView
from zope.i18n import translate
import json


class CheckProtectDossierConsistency(BrowserView):
    """
    """
    def __call__(self):
        response = self.request.response
        response.setHeader('Content-Type', 'application/json')
        response.setHeader('X-Theme-Disabled', 'True')
        response.enableHTTPCompression(REQUEST=self.request)

        return self.json()

    def json(self):
        return json.dumps(self.check_consistency())

    def check_consistency(self):
        data = {'success': True}
        if IProtectDossier(self.context).check_local_role_consistency():
            return data

        data['success'] = False
        data['text'] = translate(
            _(u'dossier_protection_inconsistency_warning',
              default="The local roles do not match with the current "
                      "dossier protection settings. If you save this "
                      "form, the local roles will be overridden."),
            context=self.request)

        return data
