from opengever.base.interfaces import IOGMailSettings
from plone import api


def is_alternative_notification_email_enabled():
    return api.portal.get_registry_record(
        'alternative_notification_email_enabled', interface=IOGMailSettings,
        default=False)


def get_notification_email(user):
    """Resolve notification recipients without changing their identity address."""
    if user is None:
        return None
    if is_alternative_notification_email_enabled():
        settings = user.user_settings
        if settings and settings.notification_email:
            return settings.notification_email
    return (user.email or '').strip() or None
