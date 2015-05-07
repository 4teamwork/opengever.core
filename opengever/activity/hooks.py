from opengever.base.model import create_session
from opengever.activity.model import DefaultSettings


DEFAULT_SETTINGS = [
    {'kind':'task-added', 'mail_notification': True},
    {'kind':'task-transition-cancelled-open', 'mail_notification': False},
    {'kind':'task-transition-delegate', 'mail_notification': False},
    {'kind':'task-transition-in-progress-resolved', 'mail_notification': False},
    {'kind':'task-transition-in-progress-tested-and-closed', 'mail_notification': False},
    {'kind':'task-transition-modify-deadline', 'mail_notification': False},
    {'kind':'task-transition-open-cancelled', 'mail_notification': False},
    {'kind':'task-transition-open-in-progress', 'mail_notification': False},
    {'kind':'task-transition-open-rejected', 'mail_notification': False},
    {'kind':'task-transition-open-resolved', 'mail_notification': False},
    {'kind':'task-transition-open-tested-and-closed', 'mail_notification': False},
    {'kind':'task-transition-reassign', 'mail_notification': True},
    {'kind':'task-transition-rejected-open', 'mail_notification': False},
    {'kind':'task-transition-resolved-in-progress', 'mail_notification': False},
    {'kind':'task-transition-resolved-tested-and-closed', 'mail_notification': False},
]


def insert_default_settings(site):
    session = create_session()
    for item in DEFAULT_SETTINGS:
        setting = DefaultSettings.query.by_kind(item.get('kind')).first()
        if not setting:
            setting = DefaultSettings(kind=item.get('kind'))
            session.add(setting)

        setting.mail_notification = item.get('mail_notification')
