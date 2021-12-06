from opengever.activity import notification_center
from opengever.base.browser.resolveoguid import ResolveOGUIDView
from opengever.base.exceptions import InvalidOguidIntIdPart
from opengever.ogds.models.service import ogds_service
from plone import api
from zExceptions import NotFound
from zExceptions import Unauthorized


class ResolveNotificationView(ResolveOGUIDView):

    key_to_strip = 'notification_id'

    def __call__(self):
        notification_id = self.request.get('notification_id', '')
        center = notification_center()
        self.notification = center.get_notification(notification_id)

        if not self.notification:
            raise NotFound('Invalid notification_id ({}) is given'.format(
                self.request.get('notification')))

        if self.notification.belongs_to(api.user.get_current()):
            self.notification.mark_as_read()

        self.redirect()

    def redirect(self):
        """Redirect to the affected resource.

        If the resource is stored in an other admin_unit than the current one,
        it redirects to the resolve_oguid view on this admin_unit.

        If there is no resource, it must be an external resource and we
        redirect to the external_resource_url.
        """
        if self.notification.activity.resource is None:
            external_url = self.notification.activity.external_resource_url
            return self.request.RESPONSE.redirect(external_url)

        oguid = self.notification.activity.resource.oguid

        if oguid.is_on_current_admin_unit:
            try:
                resource = oguid.resolve_object()
                if resource is None:
                    raise Unauthorized()
                url = resource.absolute_url()
            except InvalidOguidIntIdPart:
                raise NotFound('Requested object has been deleted')

        else:
            admin_unit = ogds_service().fetch_admin_unit(oguid.admin_unit_id)
            url = ResolveOGUIDView.url_for(oguid, admin_unit)

        return self.request.RESPONSE.redirect(self.preserve_query_string(url))
