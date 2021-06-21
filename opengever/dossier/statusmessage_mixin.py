from plone import api
from opengever.dossier import _

MSG_ALREADY_BEING_RESOLVED = _("Dossier is already being resolved")


class DossierResolutionStatusmessageMixin(object):
    """Mixin class to construct status messages and trigger redirects

    for dossier resolution errors.

    This class handles producing these status messages in a classic view
    (as opposed to the REST API, where errors are serialized as JSON).

    It takes care of:
    - Constructing the translated message(s)
    - Determining the context URL to redirect to
    - Redirecting to that context

    It is used by the DossierResolveView.
    """

    @property
    def context_url(self):
        return self.context.absolute_url()

    def redirect(self, url):
        return self.request.RESPONSE.redirect(url)

    def show_already_resolved_msg(self):
        api.portal.show_message(
            message=_('Dossier has already been resolved.'),
            request=self.request, type='info')
        return self.redirect(self.context_url)

    def show_being_resolved_msg(self):
        api.portal.show_message(
            message=MSG_ALREADY_BEING_RESOLVED,
            request=self.request, type='info')
        return self.redirect(self.context_url)

    def show_errors(self, errors):
        for msg in errors:
            api.portal.show_message(
                message=msg, request=self.request, type='error')
        return self.redirect(self.context_url)

    def show_invalid_end_dates(self, titles):
        for title in titles:
            msg = _("The dossier ${dossier} has a invalid end_date",
                    mapping=dict(dossier=title,))
            api.portal.show_message(
                message=msg, request=self.request, type='error')
        return self.redirect(self.context_url)

    def show_subdossier_resolved_msg(self):
        api.portal.show_message(
            message=_('The subdossier has been succesfully resolved.'),
            request=self.request, type='info')
        return self.redirect(self.context_url)

    def show_dossier_resolved_msg(self):
        api.portal.show_message(
            message=_('The dossier has been succesfully resolved.'),
            request=self.request, type='info')
        return self.redirect(self.context_url)
