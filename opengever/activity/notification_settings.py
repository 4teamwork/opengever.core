from opengever.activity import model
from opengever.activity.roles import COMMITTEE_RESPONSIBLE_ROLE
from opengever.activity.roles import DISPOSITION_ARCHIVIST_ROLE
from opengever.activity.roles import DISPOSITION_RECORDS_MANAGER_ROLE
from opengever.activity.roles import DOSSIER_RESPONSIBLE_ROLE
from opengever.activity.roles import PROPOSAL_ISSUER_ROLE
from opengever.activity.roles import TASK_ISSUER_ROLE
from opengever.activity.roles import TASK_REMINDER_WATCHER_ROLE
from opengever.activity.roles import TASK_RESPONSIBLE_ROLE
from opengever.activity.roles import TODO_RESPONSIBLE_ROLE
from opengever.activity.roles import WORKSPACE_MEMBER_ROLE
from opengever.base.model import create_session
from zope.i18nmessageid import MessageFactory


# We can't use the message factory from the __init__.py due to circualr imports.
_ = MessageFactory("opengever.activity")


# The NOTIFICATION_CONFIGURATION provides the configuration for the notification
# settings.
#
# The id key is the notification setting kind in the sql db.
#
# Each notification setting can map to multiple activity kinds.
NOTIFICATION_CONFIGURATION = [
    {
        'id': 'task-added-or-reassigned',
        'title': _('task-added-or-reassigned', default=u'Task added / reassigned'),
        'activities': ['task-added',
                       'task-transition-reassign',
                       'forwarding-added',
                       'forwarding-transition-reassign',
                       'forwarding-transition-reassign-refused',
                       ],
        'default_settings': {
            'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE],
            'mail_notification_roles': [TASK_RESPONSIBLE_ROLE],
        },
    },
    {
        'id': 'task-transition-modify-deadline',
        'title': _('task-transition-modify-deadline', default=u'Task deadline modified'),
        'activities': ['task-transition-modify-deadline'],
        'default_settings': {
            'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE],
        },
    },
    {
        'id': 'task-commented',
        'title': _('task-commented', default=u'Task commented'),
        'activities': ['task-commented'],
        'default_settings': {
            'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE],
        },
    },
    {
        'id': 'task-status-modified',
        'title': _('state-changed', default=u'State changed'),
        'activities': ['task-transition-cancelled-open',
                       'task-transition-rejected-open',
                       'task-transition-skipped-open',
                       'task-transition-planned-skipped',
                       'task-transition-delegate',
                       'task-transition-in-progress-resolved',
                       'task-transition-open-resolved',
                       'task-transition-in-progress-tested-and-closed',
                       'task-transition-open-cancelled',
                       'task-transition-open-in-progress',
                       'task-transition-open-rejected',
                       'task-transition-resolved-in-progress',
                       'task-transition-open-tested-and-closed',
                       'task-transition-resolved-tested-and-closed',
                       'task-transition-rejected-skipped',
                       'forwarding-transition-accept',
                       'forwarding-transition-assign-to-dossier',
                       'forwarding-transition-close',
                       'forwarding-transition-refuse',
                       ],
        'default_settings': {
            'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE],
        },
    },
    {
        'id': 'proposal-transition-reject',
        'title': _('proposal-transition-reject', default=u'Proposal rejected'),
        'activities': ['proposal-transition-reject'],
        'default_settings': {
            'badge_notification_roles': [PROPOSAL_ISSUER_ROLE],
        }
    },
    {
        'id': 'proposal-transition-schedule',
        'title': _('proposal-transition-schedule', default=u'Proposal scheduled'),
        'activities': ['proposal-transition-schedule'],
        'default_settings': {
            'badge_notification_roles': [PROPOSAL_ISSUER_ROLE],
        }
    },
    {
        'id': 'proposal-transition-pull',
        'title': _('proposal-transition-pull', default=u'Proposal pulled'),
        'activities': ['proposal-transition-pull'],
        'default_settings': {
            'badge_notification_roles': [PROPOSAL_ISSUER_ROLE],
        }
    },
    {
        'id': 'proposal-transition-decide',
        'title': _('proposal-transition-decide', default=u'Proposal decided'),
        'activities': ['proposal-transition-decide'],
        'default_settings': {
            'badge_notification_roles': [PROPOSAL_ISSUER_ROLE],
        }
    },
    {
        'id': 'proposal-transition-submit',
        'title': _('proposal-transition-submit', default=u'Proposal submitted'),
        'activities': ['proposal-transition-submit'],
        'default_settings': {
            'badge_notification_roles': [COMMITTEE_RESPONSIBLE_ROLE],
        }
    },
    {
        'id': 'proposal-commented',
        'title': _('proposal-commented', default=u'Proposal commented'),
        'activities': ['proposal-commented'],
        'default_settings': {
            'badge_notification_roles': [PROPOSAL_ISSUER_ROLE,
                                         COMMITTEE_RESPONSIBLE_ROLE],
        }
    },
    {
        'id': 'proposal-attachment-updated',
        'title': _('proposal-attachment-updated', default=u'Attachment updated'),
        'activities': ['proposal-attachment-updated'],
        'default_settings': {
            'badge_notification_roles': [COMMITTEE_RESPONSIBLE_ROLE]
        }
    },
    {
        'id': 'proposal-additional-documents-submitted',
        'title': _('proposal-additional-documents-submitted', default=u'Additional documents submitted'),
        'activities': ['proposal-additional-documents-submitted'],
        'default_settings': {
            'badge_notification_roles': [COMMITTEE_RESPONSIBLE_ROLE]
        }
    },
    {
        'id': 'task-reminder',
        'title': _('task-reminder', default=u'Task reminder'),
        'activities': ['task-reminder'],
        'default_settings': {
            'badge_notification_roles': [TASK_REMINDER_WATCHER_ROLE],
        }
    },
    {
        'id': 'disposition-added',
        'title': _('disposition-added', default=u'Disposition added'),
        'activities': ['disposition-added'],
        'default_settings': {
            'badge_notification_roles': [DISPOSITION_RECORDS_MANAGER_ROLE, DISPOSITION_ARCHIVIST_ROLE],
            'mail_notification_roles': [DISPOSITION_ARCHIVIST_ROLE],
        }
    },
    {
        'id': 'disposition-transition-appraise',
        'title': _('disposition-transition-appraise', default=u'Disposition appraised'),
        'activities': ['disposition-transition-appraise'],
        'default_settings': {
            'badge_notification_roles': [DISPOSITION_RECORDS_MANAGER_ROLE, DISPOSITION_ARCHIVIST_ROLE],
        }
    },
    {
        'id': 'disposition-transition-archive',
        'title': _('disposition-transition-archive', default=u'Disposition archived'),
        'activities': ['disposition-transition-archive'],
        'default_settings': {
            'badge_notification_roles': [DISPOSITION_RECORDS_MANAGER_ROLE, DISPOSITION_ARCHIVIST_ROLE],
        }
    },
    {
        'id': 'disposition-transition-dispose',
        'title': _('disposition-transition-dispose', default=u'Disposition disposed'),
        'activities': ['disposition-transition-dispose'],
        'default_settings': {
            'badge_notification_roles': [DISPOSITION_RECORDS_MANAGER_ROLE, DISPOSITION_ARCHIVIST_ROLE],
        }
    },
    {
        'id': 'disposition-transition-refuse',
        'title': _('disposition-transition-refuse', default=u'Disposition refused'),
        'activities': ['disposition-transition-refuse'],
        'default_settings': {
            'badge_notification_roles': [DISPOSITION_RECORDS_MANAGER_ROLE, DISPOSITION_ARCHIVIST_ROLE],
        }
    },
    {
        'id': 'disposition-transition-close',
        'title': _('disposition-transition-close', default=u'Disposition closed'),
        'activities': [
            'disposition-transition-close',
            'disposition-transition-appraised-to-closed'],
        'default_settings': {
            'badge_notification_roles': [DISPOSITION_RECORDS_MANAGER_ROLE, DISPOSITION_ARCHIVIST_ROLE],
        }
    },
    {
        'id': 'dossier-overdue',
        'title': _('dossier-overdue', default=u'Overdue dossier'),
        'activities': ['dossier-overdue'],
        'default_settings': {
            'badge_notification_roles': [DOSSIER_RESPONSIBLE_ROLE],
        }
    },
    {
        'id': 'todo-assigned',
        'title': _('todo-assigned', default=u'ToDo assigned'),
        'activities': ['todo-assigned'],
        'default_settings': {
            'badge_notification_roles': [TODO_RESPONSIBLE_ROLE],
            'digest_notification_roles': [WORKSPACE_MEMBER_ROLE],
        }
    },
    {
        'id': 'todo-modified',
        'title': _('todo-modified', default=u'ToDo modified'),
        'activities': ['todo-modified'],
        'default_settings': {
            'badge_notification_roles': [TODO_RESPONSIBLE_ROLE],
            'digest_notification_roles': [WORKSPACE_MEMBER_ROLE],
        }
    },
]


class NotificationSettings(object):
    """Object which provides functions to lookup the notification settings.
    """
    def __init__(self, configuration=NOTIFICATION_CONFIGURATION):
        self.configuration = configuration

    def get_settings(self, userid):
        """Returns the current settings for a given userid.
        """
        default_settings = self._get_default_notification_settings()
        custom_settings = self._get_custom_notification_settings(userid)

        settings = {}
        settings.update(default_settings)
        settings.update(custom_settings)

        return settings

    def get_setting(self, setting_kind, userid):
        """Returns a specific setting for a specific userid
        """
        return self.get_settings(userid).get(setting_kind)

    def get_setting_by_activity_kind(self, activity_kind, userid):
        """Each notification setting is responsible for one or multiple activities.

        This function returns the setting for a specific userid which is responsible
        for a specific activity_kind.
        """
        config = self.get_configuration_by_activity_kind(activity_kind)
        return self.get_setting(config.get('id'), userid)

    def get_configuration_by_id(self, notification_id, default=None):
        """Returns the notification configuration for a given notification id.
        """
        configuration = filter(lambda config: config.get('id') == notification_id,
                               self.configuration)

        return configuration[0] if configuration else default

    def get_configuration_by_activity_kind(self, activity_kind, default=None):
        """Returns the notification configuration which is responsible for a
        specific activity_kind.
        """
        configuration = filter(lambda config: activity_kind in config.get('activities'),
                               self.configuration)

        return configuration[0] if configuration else default

    def remove_custom_setting(self, setting_kind, userid):
        setting = self._get_custom_notification_settings(userid).get(setting_kind)
        if setting:
            create_session().delete(setting)

    def set_custom_setting(self, setting_kind, userid,
                           mail_roles=None, badge_roles=None, digest_roles=None):
        setting = self._get_custom_notification_settings(userid).get(setting_kind)
        if not setting:
            setting = model.NotificationSetting(kind=setting_kind, userid=userid)
            create_session().add(setting)

        if mail_roles is not None:
            setting.mail_notification_roles = mail_roles

        if badge_roles is not None:
            setting.badge_notification_roles = badge_roles

        if digest_roles is not None:
            setting.digest_notification_roles = digest_roles

        return setting

    def is_custom_setting(self, setting):
        """Returns true if the given setting is a custom setting.
        """
        return isinstance(setting, model.NotificationSetting)

    def _get_default_notification_settings(self):
        """Returns the default notificiation settings.
        """
        if not hasattr(self, '_default_notification_settings'):
            setattr(self, '_default_notification_settings', {
                default.kind: default for default
                in model.NotificationDefault.query
                })

        return self._default_notification_settings

    def _get_custom_notification_settings(self, userid):
        """Returns the custom notification settings for a specific userid if any
        """
        return {
            setting.kind: setting for setting
            in model.NotificationSetting.query.filter_by(userid=userid)
        }
