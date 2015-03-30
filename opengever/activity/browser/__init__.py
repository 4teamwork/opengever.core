from plone import api


def resolve_notification_url(notification):
    return "{}/@@resolve_notification?notification_id={}".format(
        api.portal.get().absolute_url(),
        notification.notification_id)
