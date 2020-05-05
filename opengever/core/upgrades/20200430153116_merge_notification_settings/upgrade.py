from opengever.activity.model import NotificationSetting
from opengever.activity.model import NotificationDefault
from opengever.activity.hooks import insert_notification_defaults
from opengever.activity.notification_settings import NotificationSettings
from opengever.core.upgrade import SchemaMigration
from plone import api


CHANNELS = (
    'badge_notification_roles',
    'mail_notification_roles',
    'digest_notification_roles',
)


class MergeNotificationSettings(SchemaMigration):
    """Merge notification settings.
    """
    def migrate(self):
        self.migrate_default_settings()
        self.migrate_custom_settings()

    def migrate_default_settings(self):
        NotificationDefault.query.delete()
        insert_notification_defaults(api.portal.get())

    def migrate_custom_settings(self):
        notification_settings = NotificationSettings()

        # Get a list of distinct userids of users that have any settings stored
        users_with_settings = [
            r[0] for r in self.session.query(NotificationSetting.userid.distinct())
        ]

        for config in notification_settings.configuration:
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
        NotificationSettings().set_custom_setting(
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
