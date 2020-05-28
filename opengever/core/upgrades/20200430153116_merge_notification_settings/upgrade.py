from opengever.activity.model import NotificationDefault
from opengever.activity.model import NotificationSetting
from opengever.activity.notification_settings import NotificationSettings
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
from opengever.core.upgrade import SchemaMigration


CHANNELS = (
    'badge_notification_roles',
    'mail_notification_roles',
    'digest_notification_roles',
)

NOTIFICATION_CONFIGURATION = [
    {
        'id': 'task-added-or-reassigned',
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
        'activities': ['task-transition-modify-deadline'],
        'default_settings': {
            'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE],
        },
    },
    {
        'id': 'task-commented',
        'activities': ['task-commented'],
        'default_settings': {
            'badge_notification_roles': [TASK_RESPONSIBLE_ROLE, TASK_ISSUER_ROLE],
        },
    },
    {
        'id': 'task-status-modified',
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
        'activities': ['proposal-transition-reject'],
        'default_settings': {
            'badge_notification_roles': [PROPOSAL_ISSUER_ROLE],
        }
    },
    {
        'id': 'proposal-transition-schedule',
        'activities': ['proposal-transition-schedule'],
        'default_settings': {
            'badge_notification_roles': [PROPOSAL_ISSUER_ROLE],
        }
    },
    {
        'id': 'proposal-transition-pull',
        'activities': ['proposal-transition-pull'],
        'default_settings': {
            'badge_notification_roles': [PROPOSAL_ISSUER_ROLE],
        }
    },
    {
        'id': 'proposal-transition-decide',
        'activities': ['proposal-transition-decide'],
        'default_settings': {
            'badge_notification_roles': [PROPOSAL_ISSUER_ROLE],
        }
    },
    {
        'id': 'proposal-transition-submit',
        'activities': ['proposal-transition-submit'],
        'default_settings': {
            'badge_notification_roles': [COMMITTEE_RESPONSIBLE_ROLE],
        }
    },
    {
        'id': 'proposal-commented',
        'activities': ['proposal-commented'],
        'default_settings': {
            'badge_notification_roles': [PROPOSAL_ISSUER_ROLE,
                                         COMMITTEE_RESPONSIBLE_ROLE],
        }
    },
    {
        'id': 'proposal-attachment-updated',
        'activities': ['proposal-attachment-updated'],
        'default_settings': {
            'badge_notification_roles': [COMMITTEE_RESPONSIBLE_ROLE]
        }
    },
    {
        'id': 'proposal-additional-documents-submitted',
        'activities': ['proposal-additional-documents-submitted'],
        'default_settings': {
            'badge_notification_roles': [COMMITTEE_RESPONSIBLE_ROLE]
        }
    },
    {
        'id': 'task-reminder',
        'activities': ['task-reminder'],
        'default_settings': {
            'badge_notification_roles': [TASK_REMINDER_WATCHER_ROLE],
        }
    },
    {
        'id': 'disposition-added',
        'activities': ['disposition-added'],
        'default_settings': {
            'badge_notification_roles': [DISPOSITION_RECORDS_MANAGER_ROLE, DISPOSITION_ARCHIVIST_ROLE],
            'mail_notification_roles': [DISPOSITION_ARCHIVIST_ROLE],
        }
    },
    {
        'id': 'disposition-transition-appraise',
        'activities': ['disposition-transition-appraise'],
        'default_settings': {
            'badge_notification_roles': [DISPOSITION_RECORDS_MANAGER_ROLE, DISPOSITION_ARCHIVIST_ROLE],
        }
    },
    {
        'id': 'disposition-transition-archive',
        'activities': ['disposition-transition-archive'],
        'default_settings': {
            'badge_notification_roles': [DISPOSITION_RECORDS_MANAGER_ROLE, DISPOSITION_ARCHIVIST_ROLE],
        }
    },
    {
        'id': 'disposition-transition-dispose',
        'activities': ['disposition-transition-dispose'],
        'default_settings': {
            'badge_notification_roles': [DISPOSITION_RECORDS_MANAGER_ROLE, DISPOSITION_ARCHIVIST_ROLE],
        }
    },
    {
        'id': 'disposition-transition-refuse',
        'activities': ['disposition-transition-refuse'],
        'default_settings': {
            'badge_notification_roles': [DISPOSITION_RECORDS_MANAGER_ROLE, DISPOSITION_ARCHIVIST_ROLE],
        }
    },
    {
        'id': 'disposition-transition-close',
        'activities': [
            'disposition-transition-close',
            'disposition-transition-appraised-to-closed'],
        'default_settings': {
            'badge_notification_roles': [DISPOSITION_RECORDS_MANAGER_ROLE, DISPOSITION_ARCHIVIST_ROLE],
        }
    },
    {
        'id': 'dossier-overdue',
        'activities': ['dossier-overdue'],
        'default_settings': {
            'badge_notification_roles': [DOSSIER_RESPONSIBLE_ROLE],
        }
    },
    {
        'id': 'todo-assigned',
        'activities': ['todo-assigned'],
        'default_settings': {
            'badge_notification_roles': [TODO_RESPONSIBLE_ROLE],
            'digest_notification_roles': [WORKSPACE_MEMBER_ROLE],
        }
    },
    {
        'id': 'todo-modified',
        'activities': ['todo-modified'],
        'default_settings': {
            'badge_notification_roles': [TODO_RESPONSIBLE_ROLE],
            'digest_notification_roles': [WORKSPACE_MEMBER_ROLE],
        }
    },
]


class MergeNotificationSettings(SchemaMigration):
    """Merge notification settings.
    """
    def migrate(self):
        self.notification_settings = NotificationSettings(NOTIFICATION_CONFIGURATION)
        self.migrate_default_settings()
        self.migrate_custom_settings()

    def migrate_default_settings(self):
        # Remove all notification defaults
        NotificationDefault.query.delete()

        # Re-add the new notification defaults
        for item in self.notification_settings.configuration:
            setting = NotificationDefault(kind=item.get('id'))
            self.session.add(setting)

            default_settings = item.get('default_settings')
            setattr(setting, 'mail_notification_roles',
                    default_settings.get('mail_notification_roles', []))
            setattr(setting, 'badge_notification_roles',
                    default_settings.get('badge_notification_roles', []))
            setattr(setting, 'digest_notification_roles',
                    default_settings.get('digest_notification_roles', []))

    def migrate_custom_settings(self):
        # Get a list of distinct userids of users that have any settings stored
        users_with_settings = [
            r[0] for r in self.session.query(NotificationSetting.userid.distinct())
        ]

        for config in self.notification_settings.configuration:
            notification_setting_kind = config.get('id')
            activities = config.get('activities')

            # If there is only one activity and is named like the notification id
            # we don't need to merge anything.
            if notification_setting_kind in activities and len(activities) == 1:
                continue

            for userid in users_with_settings:
                self.merge_custom_settings_for_user(userid, config)

    def merge_custom_settings_for_user(self, userid, config):
        """ The old settings provided one entry for each activity. The new
        implementation provides one entry for a set of activities.
        We get all entries related to notification setting and merge them together.
        """

        notification_setting_kind = config.get('id')
        activities = config.get('activities')

        custom_settings_for_activities = self.get_custom_settings_for_activities_query(
            userid, activities)
        settings_group = custom_settings_for_activities.all()

        if not custom_settings_for_activities.count():
            # Abort if we don't have any settings for the current user for
            # the current set of activities.
            return

        merged_settings = {}
        for channel in CHANNELS:
            # Determine the new roles to set. Union of all roles across
            # all activity kinds for this channel.
            new_roles = set()
            for setting in settings_group:
                for role in getattr(setting, channel):
                    new_roles.add(role)
            merged_settings[channel] = list(new_roles)

        # Delete all settings
        custom_settings_for_activities.delete(synchronize_session='fetch')

        # Add the new setting
        self.notification_settings.set_custom_setting(
            notification_setting_kind, userid,
            mail_roles=merged_settings.get('mail_notification_roles', []),
            badge_roles=merged_settings.get('badge_notification_roles', []),
            digest_roles=merged_settings.get('digest_notification_roles', []),
            )

    def get_custom_settings_for_activities_query(self, userid, activities):
        """ Returns a query for all custom notification settings for a
        specific user for a set of activities.
        """
        return NotificationSetting.query.filter_by(userid=userid).filter(
            NotificationSetting.kind.in_(activities))
