from opengever.activity.model import NotificationDefault
from opengever.base.model import create_session
from sqlalchemy.orm.exc import NoResultFound


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

    {'kind':'forwarding-transition-accept', 'mail_notification': False},
    {'kind':'forwarding-transition-assign-to-dossier', 'mail_notification': False},
    {'kind':'forwarding-transition-close', 'mail_notification': False},
    {'kind':'forwarding-transition-reassign', 'mail_notification': True},
    {'kind':'forwarding-transition-reassign-refused', 'mail_notification': True},
    {'kind':'forwarding-transition-refuse', 'mail_notification': False}
]

def insert_default_settings(site):
    session = create_session()
    for item in DEFAULT_SETTINGS:
        try:
            setting = NotificationDefault.query.by_kind(item.get('kind')).one()
        except NoResultFound:
            setting = NotificationDefault(kind=item.get('kind'))
            session.add(setting)

        setting.mail_notification = item.get('mail_notification')
