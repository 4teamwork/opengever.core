from ftw import bumblebee
from opengever.bumblebee import is_auto_refresh_enabled
from Products.CMFPlone.browser.jsvariables import JSVariables


TEMPLATE = u"{other_vars}\
var bumblebee_notification_url = '{bumblebee_notification_url}';"


class GeverJSVariables(JSVariables):
    """Expose variables to javascript

    For instance we need bumblebee's notifications URL to be
    available in the javascript part. GEVER knows how to build
    bumblebee URLs, so we expose the generated URL to javascript.
    """

    def __call__(self, *args, **kwargs):
        other_vars = super(GeverJSVariables, self).__call__(*args, **kwargs)
        notification_url = bumblebee.get_service_v3().get_notifications_url()

        if not is_auto_refresh_enabled():
            return other_vars

        return TEMPLATE.format(
            other_vars=other_vars,
            bumblebee_notification_url=notification_url)
