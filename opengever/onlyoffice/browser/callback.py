from opengever.onlyoffice.browser.base import OnlyOfficeBaseView
from plone import api
import json
import requests


class CallbackView(OnlyOfficeBaseView):

    def reply(self):
        try:
            data = json.loads(self.request.get('BODY') or '{}')
        except ValueError:
            data = {}

        status = data.get('status')
        url = data.get('url')

        with api.env.adopt_user(username=self.userid):
            if status == 1:
                self.checkout()
                self.lock()
            elif status == 2 and url:
                self.save(url)
                self.unlock()
                self.checkin()
            elif status == 4:
                self.unlock()
                self.cancel_checkout()
            elif status == 6 and url:
                self.save(url)

        return """{ "error": 0 } """

    def save(self, url):
        resp = requests.get(url, stream=True)
        with self.context.file.open(mode='w') as blob:
            for chunk in resp:
                blob.write(chunk)
