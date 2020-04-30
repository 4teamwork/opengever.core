from opengever.activity.model import NotificationDefault
from opengever.base.model import create_session
from opengever.activity.notification_settings import NotificationSettings


def insert_notification_defaults(site):
    session = create_session()
    notification_settings = NotificationSettings()
    default_notification_settings = notification_settings._get_default_notification_settings()
    for item in notification_settings.configuration:
        setting = default_notification_settings.get(item.get('id'))
        if not setting:
            setting = NotificationDefault(kind=item.get('id'))
            session.add(setting)

        default_settings = item.get('default_settings')
        setattr(setting, 'mail_notification_roles',
                default_settings.get('mail_notification_roles', []))
        setattr(setting, 'badge_notification_roles',
                default_settings.get('badge_notification_roles', []))
