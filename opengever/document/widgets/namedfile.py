from opengever.document.browser.edit import get_redirect_url
from opengever.virusscan.validator import validateDownloadStreamIfNecessary
from plone import api
from plone.formwidget.namedfile.widget import Download
from zope.interface import Invalid


class GeverNamedFileDownload(Download):
    """Download a file, via ../context/form/++widget++/@@download/filename
    but first check for viruses if necessary
    """

    def __call__(self):
        stream = super(GeverNamedFileDownload, self).__call__()
        try:
            validateDownloadStreamIfNecessary(self.filename, stream, self.request)
        except Invalid as exc:
            api.portal.show_message(exc.message, self.request, type='error')
            return self.request.RESPONSE.redirect(
                get_redirect_url(self.context.context))
        return stream
