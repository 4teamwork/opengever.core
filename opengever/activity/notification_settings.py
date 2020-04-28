from opengever.activity import model
from opengever.base.model import create_session

# The NOTIFICATION_CONFIGURATION provides the configuration for the notification
# settings.
#
# The id key is the notification setting kind in the sql db.
#
# Each notification setting can map to multiple activity kinds.
NOTIFICATION_CONFIGURATION = [
    {
        'id': 'task-added',
        'activities': ['task-added'],
    },
    {
        'id': 'task-transition-cancelled-open',
        'activities': ['task-transition-cancelled-open'],
    },
    {
        'id': 'task-transition-rejected-open',
        'activities': ['task-transition-rejected-open'],
    },
    {
        'id': 'task-transition-skipped-open',
        'activities': ['task-transition-skipped-open'],
    },
    {
        'id': 'task-transition-planned-skipped',
        'activities': ['task-transition-planned-skipped'],
    },
    {
        'id': 'task-transition-delegate',
        'activities': ['task-transition-delegate'],
    },
    {
        'id': 'task-transition-in-progress-resolved',
        'activities': ['task-transition-in-progress-resolved'],
    },
    {
        'id': 'task-transition-open-resolved',
        'activities': ['task-transition-open-resolved'],
    },
    {
        'id': 'task-transition-in-progress-tested-and-closed',
        'activities': ['task-transition-in-progress-tested-and-closed'],
    },
    {
        'id': 'task-transition-modify-deadline',
        'activities': ['task-transition-modify-deadline'],
    },
    {
        'id': 'task-transition-open-cancelled',
        'activities': ['task-transition-open-cancelled'],
    },
    {
        'id': 'task-transition-open-in-progress',
        'activities': ['task-transition-open-in-progress'],
    },
    {
        'id': 'task-transition-open-rejected',
        'activities': ['task-transition-open-rejected'],
    },
    {
        'id': 'task-commented',
        'activities': ['task-commented'],
    },
    {
        'id': 'task-transition-resolved-in-progress',
        'activities': ['task-transition-resolved-in-progress'],
    },
    {
        'id': 'task-transition-open-tested-and-closed',
        'activities': ['task-transition-open-tested-and-closed'],
    },
    {
        'id': 'task-transition-resolved-tested-and-closed',
        'activities': ['task-transition-resolved-tested-and-closed'],
    },
    {
        'id': 'task-transition-rejected-skipped',
        'activities': ['task-transition-rejected-skipped'],
    },
    {
        'id': 'forwarding-added',
        'activities': ['forwarding-added'],
    },
    {
        'id': 'forwarding-transition-accept',
        'activities': ['forwarding-transition-accept'],
    },
    {
        'id': 'forwarding-transition-assign-to-dossier',
        'activities': ['forwarding-transition-assign-to-dossier'],
    },
    {
        'id': 'forwarding-transition-close',
        'activities': ['forwarding-transition-close'],
    },
    {
        'id': 'forwarding-transition-refuse',
        'activities': ['forwarding-transition-refuse'],
    },
    {
        'id': 'task-transition-reassign',
        'activities': ['task-transition-reassign'],
    },
    {
        'id': 'forwarding-transition-reassign',
        'activities': ['forwarding-transition-reassign'],
    },
    {
        'id': 'forwarding-transition-reassign-refused',
        'activities': ['forwarding-transition-reassign-refused'],
    },
    {
        'id': 'proposal-transition-reject',
        'icon': 'rejected',
        'activities': ['proposal-transition-reject'],
    },
    {
        'id': 'proposal-transition-schedule',
        'icon': 'scheduled',
        'activities': ['proposal-transition-schedule'],
    },
    {
        'id': 'proposal-transition-pull',
        'icon': 'pulled',
        'activities': ['proposal-transition-pull'],
    },
    {
        'id': 'proposal-transition-decide',
        'icon': 'decided',
        'activities': ['proposal-transition-decide'],
    },
    {
        'id': 'proposal-transition-submit',
        'icon': 'submitted',
        'activities': ['proposal-transition-submit'],
    },
    {
        'id': 'proposal-commented',
        'icon': 'commented',
        'activities': ['proposal-commented'],
    },
    {
        'id': 'proposal-attachment-updated',
        'icon': 'documentUpdated',
        'activities': ['proposal-attachment-updated'],
    },
    {
        'id': 'proposal-additional-documents-submitted',
        'icon': 'documentAdded',
        'activities': ['proposal-additional-documents-submitted'],
    },
    {
        'id': 'task-reminder',
        'icon': 'taskReminder',
        'activities': ['task-reminder'],
    },
    {
        'id': 'disposition-added',
        'icon': 'created',
        'activities': ['disposition-added'],
    },
    {
        'id': 'disposition-transition-appraise',
        'icon': 'dispositionAppraised',
        'activities': ['disposition-transition-appraise'],
    },
    {
        'id': 'disposition-transition-archive',
        'icon': 'dispositionArchived',
        'activities': ['disposition-transition-archive'],
    },
    {
        'id': 'disposition-transition-dispose',
        'icon': 'dispositionDisposed',
        'activities': ['disposition-transition-dispose'],
    },
    {
        'id': 'disposition-transition-refuse',
        'icon': 'dispositionRefused',
        'activities': ['disposition-transition-refuse'],
    },
    {
        'id': 'disposition-transition-close',
        'icon': 'dispositionClosed',
        'activities': ['disposition-transition-close'],
    },
    {
        'id': 'disposition-transition-appraised-to-closed',
        'activities': ['disposition-transition-appraised-to-closed'],
    },
    {
        'id': 'dossier-overdue',
        'icon': 'dossierOverdue',
        'activities': ['dossier-overdue'],
    },
    {
        'id': 'todo-assigned',
        'activities': ['todo-assigned'],
    },
    {
        'id': 'todo-modified',
        'activities': ['todo-modified'],
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
