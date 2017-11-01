from opengever.activity.model import NotificationDefault
from opengever.activity.model.subscription import TASK_RESPONSIBLE_ROLE
from opengever.base.model import create_session
from sqlalchemy.orm.exc import NoResultFound


DEFAULT_SETTINGS = [
    {'kind': 'task-added',
     'mail_notification_roles': [TASK_RESPONSIBLE_ROLE]},
    {'kind': 'task-transition-cancelled-open'},
    {'kind': 'task-transition-delegate'},
    {'kind': 'task-transition-in-progress-resolved'},
    {'kind': 'task-transition-in-progress-tested-and-closed'},
    {'kind': 'task-transition-modify-deadline'},
    {'kind': 'task-transition-open-cancelled'},
    {'kind': 'task-transition-open-in-progress'},
    {'kind': 'task-transition-open-rejected'},
    {'kind': 'task-transition-open-resolved'},
    {'kind': 'task-transition-open-tested-and-closed'},
    {'kind': 'task-commented'},
    {'kind': 'task-transition-reassign',
     'mail_notification_roles': [TASK_RESPONSIBLE_ROLE]},
    {'kind': 'task-transition-rejected-open'},
    {'kind': 'task-transition-resolved-in-progress'},
    {'kind': 'task-transition-resolved-tested-and-closed'},
    {'kind': 'forwarding-added',
     'mail_notification_roles': [TASK_RESPONSIBLE_ROLE]},
    {'kind': 'forwarding-transition-accept'},
    {'kind': 'forwarding-transition-assign-to-dossier'},
    {'kind': 'forwarding-transition-close'},
    {'kind': 'forwarding-transition-reassign',
     'mail_notification_roles': [TASK_RESPONSIBLE_ROLE]},
    {'kind': 'forwarding-transition-reassign-refused',
     'mail_notification_roles': [TASK_RESPONSIBLE_ROLE]},
    {'kind': 'forwarding-transition-refuse', 'mail_notification': False}
]


def insert_notification_defaults(site):
    session = create_session()
    for item in DEFAULT_SETTINGS:
        try:
            setting = NotificationDefault.query.by_kind(item.get('kind')).one()
        except NoResultFound:
            setting = NotificationDefault(kind=item.get('kind'))
            session.add(setting)

        setting.set_mail_notification_roles(
            item.get('mail_notification_roles', []))
