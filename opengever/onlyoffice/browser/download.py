from opengever.onlyoffice.browser.base import OnlyOfficeBaseView
from plone import api
from plone.namedfile.utils import set_headers
from plone.namedfile.utils import stream_data


class DownloadView(OnlyOfficeBaseView):

    def reply(self):

        with api.env.adopt_user(username=self.userid):
            self.checkout()
            self.lock()
            file_ = self.context.file
            set_headers(file_, self.request.response, filename=file_.filename)
            return stream_data(file_)
