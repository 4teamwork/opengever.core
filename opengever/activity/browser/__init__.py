from opengever.ogds.base.utils import get_current_admin_unit


def resolve_notification_url(notification):
    return "{}/@@resolve_notification?notification_id={}".format(
        get_current_admin_unit().public_url,
        notification.notification_id)
