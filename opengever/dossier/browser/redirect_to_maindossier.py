from opengever.dossier import _
from opengever.dossier.utils import get_main_dossier
from plone import api
from Products.Five.browser import BrowserView


class RedirectToMainDossier(BrowserView):
    """Redirects to the main dossier of any content.

    Caution: this view will be used by GEVER-UI/RIS/VM
    """
    def __call__(self):
        main_dossier = get_main_dossier(self.context)
        if not main_dossier:
            msg = _(u'msg_main_dossier_not_found',
                    default=u'The object `${title}` is not stored inside a dossier.',
                    mapping={'title': self.context.Title().decode('utf-8')})
            api.portal.show_message(msg, request=self.request, type='error')
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        url_parts = [main_dossier.absolute_url()]
        qs = self.request['QUERY_STRING']
        if qs:
            url_parts.append(qs)
        redirect_url = '?'.join(url_parts)
        return self.request.RESPONSE.redirect(redirect_url)
