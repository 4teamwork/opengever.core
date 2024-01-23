from opengever.ris import RIS_VIEW_EDIT
from opengever.ris.interfaces import IRisSettings
from plone import api
from Products.Five import BrowserView


class EditInRisView(BrowserView):

    def __call__(self):
        ris_url = api.portal.get_registry_record(
            name='base_url', interface=IRisSettings
        ).rstrip("/")
        ris_edit_url = '{}/{}?context={}'.format(
            ris_url,
            RIS_VIEW_EDIT,
            self.context.absolute_url(),)

        return self.request.RESPONSE.redirect(ris_edit_url)
