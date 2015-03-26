from five import grok
from opengever.activity import notification_center
from opengever.base.browser.resolveoguid import ResolveOGUIDView
from opengever.ogds.base.utils import ogds_service
from plone import api
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zExceptions import NotFound
from zExceptions import Unauthorized


class ResolveNotificationView(ResolveOGUIDView):
    grok.name('resolve_notification')
    grok.context(IPloneSiteRoot)
    grok.require('zope2.View')

    def render(self):
        notification_id = self.request.get('notification_id', '')
        center = notification_center()
        self.notification = center.get_notification(notification_id)

        if not self.notification:
            raise NotFound('Invalid notification_id ({}) is given'.format(
                self.request.get('notification')))

        if not self.check_permission():
            raise Unauthorized()

        self.mark_as_read()
        self.redirect()

    def check_permission(self):
        """Check if the current user is allowed to view the notification."""

        current_user = api.user.get_current()
        return self.notification.watcher.user_id == current_user.getId()

    def mark_as_read(self):
        self.notification.read = True

    def redirect(self):
        """Redirect to the affected resource. If the resource is stored
        in an other admin_unit than the current one, it redirects to the
        resolve_oguid view on this admin_unit."""

        oguid = self.notification.activity.resource.oguid

        if oguid.is_on_current_admin_unit:
            url = oguid.resolve_object().absolute_url()

        else:
            admin_unit = ogds_service().fetch_admin_unit(oguid.admin_unit_id)
            url = ResolveOGUIDView.url_for(oguid, admin_unit)

        return self.request.RESPONSE.redirect(url)
