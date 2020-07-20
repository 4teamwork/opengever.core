from AccessControl import getSecurityManager
from base64 import urlsafe_b64encode
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.wopi import _
from opengever.wopi.discovery import actions_by_extension
from opengever.wopi.interfaces import IWOPISettings
from opengever.wopi.token import create_access_token
from plone import api
from plone.uuid.interfaces import IUUID
from Products.Five.browser import BrowserView
from time import time
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
import logging


logger = logging.getLogger('opengever.wopi')


class EditOnlineView(BrowserView):

    def __call__(self):
        if self.is_exclusively_checked_out():
            logger.error(
                'Attempt to edit %r with Office Online even though it is '
                'already checked out for exclusive editing ' % self.context)
            api.portal.show_message(
                _(u'Document is checked out for exclusive editing.'),
                self.request, 'error')
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        actions = actions_by_extension()
        ext = self.context.file.filename.split('.')[-1]
        action = actions[ext]['edit']
        self.favicon_url = action['favicon_url']
        urlsrc = action['urlsrc']

        uuid = IUUID(self.context)
        user = getSecurityManager().getUser()

        self.track_additional_collaborator_if_needed(user)

        self.access_token = urlsafe_b64encode(
            create_access_token(user.getId(), uuid))
        self.access_token_ttl = int(time() + 43200) * 1000

        self.params = {
            'UI_LLCC': 'de-DE',
            'DC_LLCC': 'de-DE',
            'DISABLE_CHAT': '1',
            'BUSINESS_USER': '0',
        }

        if api.portal.get_registry_record(
            name='business_user', interface=IWOPISettings
        ):
            self.params['BUSINESS_USER'] = '1'

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

    def is_exclusively_checked_out(self):
        manager = getMultiAdapter((self.context, self.request),
                                  ICheckinCheckoutManager)
        return (manager.get_checked_out_by()
                and not manager.is_collaborative_checkout())

    def track_additional_collaborator_if_needed(self, user):
        """If user joins a collaborative editing session, track them.

        The MS WOPI client sometimes doesn't send the X-WOPI-Editors
        header. We therefore also track collaborators here.

        But only for additional users that join a collaborative editing
        session - the user that initially checks out the document should
        already have been added as a collaborator.
        """
        manager = getMultiAdapter((self.context, self.request),
                                  ICheckinCheckoutManager)
        if manager.get_checked_out_by() and manager.is_collaborative_checkout():
            manager.add_collaborator(user.getId())
