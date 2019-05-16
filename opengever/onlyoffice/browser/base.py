from base64 import urlsafe_b64decode
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.onlyoffice.token import validate_access_token
from plone.locking.interfaces import ILockable
from plone.locking.interfaces import IRefreshableLockable
from plone.uuid.interfaces import IUUID
from Products.Five.browser import BrowserView
from urlparse import parse_qs
from zope.component import getMultiAdapter


class OnlyOfficeBaseView(BrowserView):

    def __call__(self):
        qs = parse_qs(self.request.get('QUERY_STRING'))
        token = qs.get('access_token', [''])[0]
        try:
            token = urlsafe_b64decode(token)
        except:
            token = None
        self.userid = validate_access_token(token, IUUID(self.context))
        if not self.userid:
            self.request.response.setStatus(401)
            return "Unauthorized"
        return self.reply()

    def reply(self):
        raise NotImplementedError

    def checkout(self):
        manager = getMultiAdapter((self.context, self.request),
                                  ICheckinCheckoutManager)
        if not manager.get_checked_out_by():
            manager.checkout()

    def checkin(self):
        manager = getMultiAdapter((self.context, self.request),
                                  ICheckinCheckoutManager)
        manager.checkin()

    def cancel_checkout(self):
        manager = getMultiAdapter((self.context, self.request),
                                  ICheckinCheckoutManager)
        manager.cancel()

    def lock(self):
        lockable = IRefreshableLockable(self.context, None)
        if lockable is not None:
            lockable.lock()

    def unlock(self):
        lockable = ILockable(self.context)
        if lockable.can_safely_unlock():
            lockable.unlock()
