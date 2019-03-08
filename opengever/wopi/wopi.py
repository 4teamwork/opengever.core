from AccessControl import getSecurityManager
from plone import api
from plone.app.uuid.utils import uuidToObject
from plone.locking.interfaces import IRefreshableLockable
from plone.locking.interfaces import STEALABLE_LOCK
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.utils import set_headers
from plone.namedfile.utils import stream_data
from Products.Five.browser import BrowserView
from webdav.LockItem import LockItem
from zExceptions import NotFound as zNotFound
from ZODB.utils import u64
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound
import json


@implementer(IPublishTraverse)
class WOPIView(BrowserView):

    def __init__(self, context, request):
        super(WOPIView, self).__init__(context, request)
        self.endpoint = None
        self.object_id = None
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
        print self.request.ACTUAL_URL + '?' + self.request.get('QUERY_STRING')
        lock = self.request.getHeader('X-WOPI-Lock', '-')
        old_lock = self.request.getHeader('X-WOPI-OldLock', '-')
        print "Method: {}, X-WOPI-Override: {}, X-WOPI-Lock: {}, X-WOPI-OldLock: {}".format(
            self.method, self.override, lock, old_lock)
        print ""

        access_token = self.request.form.get('access_token')
        if access_token != 'secret':
            self.request.response.setStatus(401)
            return "Unauthorized"

        if self.object_id is None:
            raise zNotFound()

        if self.endpoint == 'files':
            if self.operation is None:
                if self.method == 'GET':
                    return self.check_file_info()
                elif self.method == 'POST':
                    if self.override == 'LOCK':
                        return self.lock()
                    elif self.override == 'UNLOCK':
                        return self.unlock()
                    elif self.override == 'REFRESH_LOCK':
                        return self.lock()
                    elif self.override == 'GET_LOCK':
                        return self.get_lock()
            elif self.operation == 'contents':
                if self.method == 'GET':
                    return self.get_file()
                elif self.method == 'POST':
                    if self.override == 'PUT':
                        return self.put_file()

        raise zNotFound()

    def render_json(self, data):
        self.request.response.setHeader("Content-Type", 'application/json')
        return json.dumps(
            data, indent=2, sort_keys=True, separators=(', ', ': '))

    def obj(self):
        obj = uuidToObject(self.object_id)
        if obj is None:
            raise zNotFound()
        return obj

    def check_file_info(self):
        with api.env.adopt_user(username='thomas.buchberger'):
            obj = self.obj()
            member = self.portal_state.member()
            data = {
                'BaseFileName': obj.file.filename,
                'OwnerId': obj.Creator(),
                'Size': obj.file.size,
                'UserId': member.getId(),
                # 'Version': str(obj.get_current_version_id()),
                'Version': str(u64(obj.file._blob._p_serial)),
                'UserFriendlyName': member.getProperty('fullname') or member.getId(),
                'SupportsUpdate': True,
                'SupportsLocks': True,
                'SupportsGetLock': True,
                'UserCanNotWriteRelative': True,
                'UserCanWrite': True,
                'CloseUrl': obj.absolute_url(),
            }
        return self.render_json(data)

    def get_file(self):
        with api.env.adopt_user(username='thomas.buchberger'):
            obj = self.obj()
        file_ = obj.file

        set_headers(file_, self.request.response, filename=file_.filename)
        return stream_data(file_)

    def put_file(self):
        with api.env.adopt_user(username='thomas.buchberger'):
            obj = self.obj()
            lockable = IRefreshableLockable(obj, None)
            if lockable is not None:
                lock_info = lockable.lock_info()
                if lock_info:
                    current_token = lock_info[0]['token']
                    token = self.request.getHeader('X-WOPI-Lock')
                    # Office Online sends the wrong token?!!
                    # if current_token != token:
                    #     self.request.response.setStatus(409)
                    #     self.request.response.setHeader('X-WOPI-Lock', token)
                    #     return
                    filename = obj.file.filename
                    content_type = obj.file.contentType
                    self.request.stdin.seek(0)
                    data = self.request.stdin.read()
                    obj.file = NamedBlobFile(
                        data=data, filename=filename,
                        contentType=content_type)
                    self.request.response.setStatus(200, lock=1)
                else:
                    self.request.response.setStatus(409)
                    self.request.response.setHeader('X-WOPI-Lock', token)
                    return
            else:
                self.request.response.setStatus(501)

    def lock(self):
        with api.env.adopt_user(username='thomas.buchberger'):
            obj = self.obj()
            lockable = IRefreshableLockable(obj, None)
            if lockable is not None:
                lock_info = lockable.lock_info()
                if lock_info:
                    current_token = lock_info[0]['token']
                    old_token = self.request.getHeader('X-WOPI-OldLock')
                    token = self.request.getHeader('X-WOPI-Lock')
                    # UnlockAndRelock operation
                    if old_token:
                        if current_token == old_token:
                            lockable.unlock()
                            self.create_lock(obj, token)
                        else:
                            self.request.response.setStatus(409)
                            self.request.response.setHeader('X-WOPI-Lock', token)
                            return
                    # Lock/RefreshLock operation
                    else:
                        if current_token != token:
                            self.request.response.setStatus(409)
                            self.request.response.setHeader('X-WOPI-Lock', token)
                            return
                        lockable.refresh_lock()
                else:
                    token = self.request.getHeader('X-WOPI-Lock')
                    self.create_lock(obj, token)
                self.request.response.setStatus(200, lock=1)
            else:
                self.request.response.setStatus(501)

    def create_lock(self, obj, token):
        """Create a lock with a custom token."""
        user = getSecurityManager().getUser()
        lock = LockItem(user, depth=0, timeout=1800, token=token)
        obj.wl_setLock(token, lock)
        lockable = IRefreshableLockable(obj, None)
        locks = lockable._locks()
        locks[STEALABLE_LOCK.__name__] = dict(type=STEALABLE_LOCK, token=token)

    def unlock(self):
        token = self.request.getHeader('X-WOPI-Lock')
        with api.env.adopt_user(username='thomas.buchberger'):
            obj = self.obj()
            lockable = IRefreshableLockable(obj, None)
            if lockable is not None:
                lock_info = lockable.lock_info()
                if lock_info:
                    if lock_info[0]['token'] != token:
                        self.request.response.setStatus(409)
                        self.request.response.setHeader(
                            'X-WOPI-Lock', lock_info[0]['token'])
                        return
                    lockable.unlock()
                self.request.response.setStatus(200, lock=1)
            else:
                self.request.response.setStatus(501)

    def get_lock(self):
        with api.env.adopt_user(username='thomas.buchberger'):
            obj = self.obj()
            lockable = IRefreshableLockable(obj, None)
            if lockable is not None:
                lock_info = lockable.lock_info()
                if lock_info:
                    token = lock_info[0]['token']
                    self.request.response.setHeader('X-WOPI-Lock', token)
                else:
                    self.request.response.setHeader('X-WOPI-Lock', '')
                self.request.response.setStatus(200, lock=1)
            else:
                self.request.response.setStatus(501)
