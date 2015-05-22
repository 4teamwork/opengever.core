from OFS.CopySupport import cookie_path
from plone.app.uuid.utils import uuidToObject
from plone.uuid.interfaces import IUUID
import json


class Clipboard(object):

    key = '_clipboard'

    def __init__(self, request):
        self.request = request

    def set_objs(self, objs):
        uuids = [IUUID(obj) for obj in objs]
        value = json.dumps(uuids).encode('base64')
        self.request.RESPONSE.setCookie(
            self.key, value, path=str(cookie_path(self.request)))

    def get_objs(self):
        value = self.request.cookies.get(self.key)
        if value:
            uuids = json.loads(value.decode('base64'))
            return [uuidToObject(uuid) for uuid in uuids]

        return None

    def cookie_path(self):
        # Return a "path" value for use in a cookie that refers
        # to the root of the Zope object space.
        return self.request['BASEPATH1'] or "/"
