from Acquisition import aq_parent
from base64 import urlsafe_b64encode
from opengever.onlyoffice.config import PRESENTATION_TYPES
from opengever.onlyoffice.config import SPREADSHEET_TYPES
from opengever.onlyoffice.config import TEXT_TYPES
from opengever.onlyoffice.interfaces import IOnlyOfficeSettings
from opengever.onlyoffice.token import create_access_token
from plone import api
from plone.uuid.interfaces import IUUID
from Products.Five.browser import BrowserView
import codecs
import json
import os.path
import struct


class EditView(BrowserView):
    """Renders the embedded online editor"""

    def __call__(self):
        return self.index()

    def key(self):
        # key is limited to 20 base64 chars (15 bytes) and must be unique for
        # every document version. We use 7 bytes from the UUID and the
        # modification time packed as 8 bytes
        mtime = struct.pack('>d', self.context.file._blob._p_mtime)
        uuid = codecs.decode(IUUID(self.context), 'hex_codec')
        return urlsafe_b64encode(uuid[:7] + mtime)

    def api_url(self):
        return api.portal.get_registry_record(
            name='documentserver_api_url', interface=IOnlyOfficeSettings)

    def document_type(self):
        basename, extension = os.path.splitext(self.context.file.filename)
        if extension in TEXT_TYPES:
            return 'text'
        elif extension in SPREADSHEET_TYPES:
            return 'spreadsheet'
        elif extension in PRESENTATION_TYPES:
            return 'presentation'

    def device_type(self):
        user_agent = self.request.getHeader('User-Agent', '')
        if 'Mobile' in user_agent:
            return 'mobile'
        else:
            return 'desktop'

    def js_snippet(self):
        user = api.user.get_current()
        userid = user.getId()

        token = urlsafe_b64encode(
            create_access_token(userid, IUUID(self.context)))
        download_url = '{}/onlyoffice_download?access_token={}'.format(
            self.context.absolute_url(), token)
        callback_url = '{}/onlyoffice_callback?access_token={}'.format(
            self.context.absolute_url(), token)

        config = {
            "document": {
                "fileType": self.context.file.filename.rsplit('.', 1)[-1],
                "key": self.key(),
                "title": self.context.Title(),
                "url": download_url,
                "info": {
                    "author": self.context.Creator(),
                    "created": self.context.created().ISO(),
                    "folder": aq_parent(self.context).Title(),
                }
            },
            "documentType": self.document_type(),
            "type": self.device_type(),
            "editorConfig": {
                "callbackUrl": callback_url,
                "lang": "de-CH",
                "mode": "edit",
                "user": {
                    "id": userid,
                    "name": user.getProperty('fullname') or userid,
                },
                "customization": {
                    "goback": {
                        "blank": False,
                        "text": "Back to GEVER",
                        "url": self.context.absolute_url(),
                    },
                },
            },
        }
        return JS_SNIPPET.format(json.dumps(config))


JS_SNIPPET = """
var config = {};
var docEditor = new DocsAPI.DocEditor("editor-placeholder", config);
"""
