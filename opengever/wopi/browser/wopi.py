from Acquisition import aq_parent
from base64 import urlsafe_b64decode
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.wopi.lock import create_lock
from opengever.wopi.lock import get_lock_token
from opengever.wopi.lock import refresh_lock
from opengever.wopi.lock import unlock
from opengever.wopi.lock import validate_lock
from opengever.wopi.token import validate_access_token
from plone import api
from plone.app.uuid.utils import uuidToObject
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.utils import set_headers
from plone.namedfile.utils import stream_data
from Products.Five.browser import BrowserView
from zExceptions import NotFound as zNotFound
from ZODB.utils import u64
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound
import json
import logging


logger = logging.getLogger('opengever.wopi')

_marker = object()


@implementer(IPublishTraverse)
class WOPIView(BrowserView):

    def __init__(self, context, request):
        super(WOPIView, self).__init__(context, request)
        self.endpoint = None
        self.object_id = None
        self._obj = _marker
        self.operation = None
        self.method = request.get('REQUEST_METHOD')
        self.override = request.getHeader('X-WOPI-Override')
        self.portal_state = queryMultiAdapter(
            (self.context, self.request), name=u'plone_portal_state')

    def publishTraverse(self, request, name):
        if self.endpoint is None:
            self.endpoint = name
        elif self.object_id is None:
            self.object_id = name
        elif self.operation is None:
            self.operation = name
        else:
            raise NotFound(self, name, request)
        return self

    def __call__(self):
        if self.object_id is None:
            raise zNotFound()

        token = self.request.form.get('access_token', '')
        try:
            token = urlsafe_b64decode(token)
        except TypeError:
            token = None
        userid = validate_access_token(token, self.object_id)
        if not userid:
            self.request.response.setStatus(401)
            return "Unauthorized"

        operation = None
        if self.endpoint == 'files':
            if self.operation is None:
                if self.method == 'GET':
                    operation = 'check_file_info'
                elif self.method == 'POST':
                    if self.override == 'LOCK':
                        if self.request.getHeader('X-WOPI-OldLock'):
                            operation = 'unlock_and_relock'
                        else:
                            operation = 'lock'
                    elif self.override == 'UNLOCK':
                        operation = 'unlock'
                    elif self.override == 'REFRESH_LOCK':
                        operation = 'refresh_lock'
                    elif self.override == 'GET_LOCK':
                        operation = 'get_lock'
                    elif self.override == 'PUT_RELATIVE':
                        operation = 'put_relative_file'
            elif self.operation == 'contents':
                if self.method == 'GET':
                    operation = 'get_file'
                elif self.method == 'POST':
                    if self.override == 'PUT':
                        operation = 'put_file'

        if operation is None:
            self.request.response.setStatus(400)
            return

        operation_name = ''.join([o.title() for o in operation.split('_')])
        logger.debug('WOPI Operation: %s', operation_name)

        method = getattr(self, operation)
        with api.env.adopt_user(username=userid):
            return method()

    def render_json(self, data):
        self.request.response.setHeader("Content-Type", 'application/json')
        return json.dumps(
            data, indent=2, sort_keys=True, separators=(', ', ': '))

    @property
    def obj(self):
        if self._obj is not _marker:
            return self._obj
        self._obj = uuidToObject(self.object_id)
        if self._obj is None:
            raise zNotFound()
        return self._obj

    def check_file_info(self):
        member = self.portal_state.member()
        dossier = aq_parent(self.obj)
        modified_dt = self.obj.modified().asdatetime()
        modified_iso9601 = (
            modified_dt.replace(tzinfo=None) - modified_dt.utcoffset()
            ).isoformat() + 'Z'
        data = {
            'BaseFileName': self.obj.file.filename,
            'OwnerId': self.obj.Creator(),
            'Size': self.obj.file.size,
            'UserId': member.getId(),
            'Version': self._file_version(),
            'UserFriendlyName': member.getProperty('fullname') or member.getId(),
            'SupportsUpdate': True,
            'SupportsLocks': True,
            'SupportsGetLock': True,
            'UserCanNotWriteRelative': True,
            'UserCanWrite': True,
            'CloseUrl': self.obj.absolute_url(),
            'BreadcrumbBrandName': 'OneGov GEVER',
            'BreadcrumbBrandUrl': self.portal_state.portal_url(),
            'BreadcrumbDocName': self.obj.Title(),
            'BreadcrumbFolderName': dossier.Title(),
            'BreadcrumbFolderUrl': dossier.absolute_url(),
            'LastModifiedTime': modified_iso9601,
        }
        return self.render_json(data)

    def get_file(self):
        file_ = self.obj.file
        self.request.response.setHeader(
            'X-WOPI-ItemVersion', self._file_version())
        set_headers(file_, self.request.response, filename=file_.filename)
        return stream_data(file_)

    def lock(self):
        current_token = get_lock_token(self.obj)
        if current_token:
            token = self.request.getHeader('X-WOPI-Lock')
            if not validate_lock(current_token, token):
                self.request.response.setStatus(409)
                self.request.response.setHeader('X-WOPI-Lock', current_token)
                return
            refresh_lock(self.obj)
        else:
            self.checkout()
            token = self.request.getHeader('X-WOPI-Lock')
            create_lock(self.obj, token)
            self.request.response.setHeader(
                'X-WOPI-ItemVersion', self._file_version())
        self.request.response.setStatus(200, lock=1)

    def get_lock(self):
        token = get_lock_token(self.obj)
        if token is not None:
            self.request.response.setHeader('X-WOPI-Lock', token)
        else:
            self.request.response.setHeader('X-WOPI-Lock', '')
        self.request.response.setStatus(200, lock=1)

    refresh_lock = lock

    def unlock(self):
        token = self.request.getHeader('X-WOPI-Lock')
        current_token = get_lock_token(self.obj)
        if current_token is None or current_token != token:
            self.request.response.setStatus(409)
            self.request.response.setHeader(
                'X-WOPI-Lock', current_token or '')
            return
        unlock(self.obj)
        self.checkin()
        self.request.response.setHeader(
            'X-WOPI-ItemVersion', self._file_version())
        self.request.response.setStatus(200, lock=1)

    def unlock_and_relock(self):
        current_token = get_lock_token(self.obj)
        if current_token:
            old_token = self.request.getHeader('X-WOPI-OldLock')
            token = self.request.getHeader('X-WOPI-Lock')
            if validate_lock(current_token, old_token):
                unlock(self.obj)
                create_lock(self.obj, token)
                self.request.response.setStatus(200, lock=1)
            else:
                self.request.response.setStatus(409)
                self.request.response.setHeader('X-WOPI-Lock', current_token)
                return

    def put_file(self):
        current_token = get_lock_token(self.obj)
        if current_token is not None:
            token = self.request.getHeader('X-WOPI-Lock')
            if not validate_lock(current_token, token, strict=False):
                logger.warn(
                    'Lock token mismatch: current token: %s, '
                    'provided token: %s', current_token, token)
                self.request.response.setStatus(409)
                self.request.response.setHeader('X-WOPI-Lock', current_token)
                return
            self._put_file()
        else:
            if self.obj.file.size == 0:
                self._put_file()
            else:
                self.request.response.setStatus(409)
                self.request.response.setHeader('X-WOPI-Lock', '')

    def put_relative_file(self):
        # Not implemented
        self.request.response.setStatus(501)

    def checkout(self):
        manager = getMultiAdapter((self.obj, self.request),
                                  ICheckinCheckoutManager)
        if not manager.get_checked_out_by():
            manager.checkout(collaborative=True)

    def checkin(self):
        manager = getMultiAdapter((self.obj, self.request),
                                  ICheckinCheckoutManager)
        manager.checkin(collaborative=True)

    def _file_version(self):
        # The current version of the file.
        # This value must change when the file changes, and version values must
        # never repeat for a given file. Thus we use the ZODB transaction id.
        version = str(u64(self.obj.file._blob._p_serial))
        if version == '0':
            version = str(u64(self.obj._p_serial))
        return version

    def _put_file(self):
        filename = self.obj.file.filename
        content_type = self.obj.file.contentType
        self.request.stdin.seek(0)
        data = self.request.stdin.read()
        self.obj.file = NamedBlobFile(
            data=data, filename=filename,
            contentType=content_type)
        self.request.response.setHeader(
            'X-WOPI-ItemVersion', self._file_version())
        logger.info('X-WOPI-ItemVersion: %s', self._file_version())

        # Track collaborators
        editors = self.request.getHeader('X-WOPI-Editors')
        if editors is None:
            logger.warn('X-WOPI-Editors header is missing')
        else:
            editors = [ed.strip() for ed in editors.split(',')]
            manager = getMultiAdapter((self.obj, self.request),
                                      ICheckinCheckoutManager)
            for editor in editors:
                manager.add_collaborator(editor)

        self.request.response.setStatus(200, lock=1)
