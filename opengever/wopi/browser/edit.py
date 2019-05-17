from AccessControl import getSecurityManager
from base64 import urlsafe_b64encode
from opengever.wopi.discovery import actions_by_extension
from opengever.wopi.token import create_access_token
from plone.uuid.interfaces import IUUID
from Products.Five.browser import BrowserView
from time import time
from zope.component import queryMultiAdapter


class EditOnlineView(BrowserView):

    def __call__(self):

        actions = actions_by_extension()
        ext = self.context.file.filename.split('.')[-1]
        action = actions[ext]['edit']
        self.favicon_url = action['favicon_url']
        urlsrc = action['urlsrc']

        uuid = IUUID(self.context)
        user = getSecurityManager().getUser()
        self.access_token = urlsafe_b64encode(
            create_access_token(user.getId(), uuid))
        self.access_token_ttl = int(time() + 43200) * 1000

        self.params = {
            'UI_LLCC': 'de-DE',
            'DC_LLCC': 'de-DE',
            'DISABLE_CHAT': '1',
            'BUSINESS_USER': '0',
        }

        url, qs = urlsrc.split('?')
        params = qs.split('><')
        params = [p.lstrip('<').rstrip('>') for p in params]
        params_with_values = []
        for param in params:
            placeholder = param.split('=')[1].rstrip('&')
            if placeholder in self.params:
                params_with_values.append(
                    param.replace(placeholder, self.params[placeholder]))

        portal_state = queryMultiAdapter(
            (self.context, self.request), name=u'plone_portal_state')
        wopi_src = '{}/wopi/files/{}'.format(portal_state.portal_url(), uuid)
        params_with_values.append('WOPISrc={}&'.format(wopi_src))
        self.urlsrc = '?'.join([url, ''.join(params_with_values)])

        return self.index()
