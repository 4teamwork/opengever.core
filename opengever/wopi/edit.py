from Products.Five.browser import BrowserView
from zope.component import queryMultiAdapter
from plone.uuid.interfaces import IUUID
from opengever.wopi.discovery import actions_by_extension


class EditOnlineView(BrowserView):

    def __call__(self):

        actions = actions_by_extension()
        ext = self.context.file.filename.split('.')[-1]
        action = actions[ext]['edit']
        self.favicon_url = action['favicon_url']
        urlsrc = action['urlsrc']
        self.access_token = 'secret'
        self.access_token_ttl = 0

        self.params = {
            'UI_LLCC': 'en-US',
            'DC_LLCC': 'en-US',
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
        wopi_src = '{}/wopi/files/{}'.format(
            portal_state.portal_url(), IUUID(self.context))
        params_with_values.append('WOPISrc={}&'.format(wopi_src))
        self.urlsrc = '?'.join([url, ''.join(params_with_values)])

        return self.index()
