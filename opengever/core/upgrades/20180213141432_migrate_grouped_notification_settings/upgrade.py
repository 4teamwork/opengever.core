from opengever.activity.model import NotificationDefault
from opengever.activity.model import NotificationSetting
from opengever.base.model import create_session
from opengever.core.upgrade import SchemaMigration
import logging


log = logging.getLogger('ftw.upgrade')


ALIASED_SETTINGS = {
    'task-transition-in-progress-tested-and-closed': (
        'task-transition-in-progress-tested-and-closed',
        'task-transition-open-tested-and-closed',
        'task-transition-resolved-tested-and-closed',
    ),
    'task-transition-in-progress-resolved': (
        'task-transition-in-progress-resolved',
        'task-transition-open-resolved',
    ),
    'task-transition-cancelled-open': (
        'task-transition-cancelled-open',
        'task-transition-rejected-open',
    ),
}


CHANNELS = (
    'badge_notification_roles',
    'mail_notification_roles',
    'digest_notification_roles',
)


class MigrateGroupedNotificationSettings(SchemaMigration):
    """Migrate grouped notification settings (alias groups).

    This is required because if the settings for aliased groups aren't
    homogenous for a specific alias group, the UI might show different
    settings than those that will actually be used.

    Implemented as a "schema migration" because this ensures this upgrade
    step is only executed once per cluster, and therefore shouldn't be
    affected by actual schema migrations.
    """

    def migrate(self):
        log.info("Migrating notification settings for aliased groups...")
        self.session = create_session()
        self.new_settings_to_insert = {}

        # Determine notification defaults *once*, ahead of time
        self.notification_defaults = {
            default.kind: default for default in NotificationDefault.query}

        # Get a list of distinct userids of users that have any settings stored
        users_with_settings = [
            r[0] for r in self.session.query(
                NotificationSetting.userid.distinct())
        ]

        # For each user, homogenize their settings
        for userid in users_with_settings:
            self.homogenize_settings(userid)

        # Finally, add any new setting rows that were missing (necessary where
        # only some kinds of an alias group had non-default settings)
        self.insert_newly_required_settings()
        log.info("Done migrating notification settings for aliased groups")

    def homogenize_settings(self, userid):
        """For each group of aliased kinds, make sure they all have the same
        roles ticked for a given channel. We set the ticked roles to the
        union of all roles across the alias group.
        """
        for alias_group in ALIASED_SETTINGS.values():
            settings_group = NotificationSetting.query.filter_by(
                userid=userid).filter(
                    NotificationSetting.kind.in_(alias_group)).all()

            for channel in CHANNELS:

                # Determine the new roles to set. Union of all roles across
                # all aliased kinds for this channel.
                new_roles = set()
                for setting in settings_group:
                    for role in getattr(setting, channel):
                        new_roles.add(role)
                new_roles = list(new_roles)

                # Update existing settings with the new roles
                self.update_existing_settings(
                    userid, settings_group, channel, new_roles)

                # Check if any new setting rows are needed. These are necessary
                # where only *some* kinds of an alias group had non-default
                # settings, but not all
                self.prepare_newly_required_settings(
                    userid, alias_group, settings_group, channel, new_roles)

    def prepare_newly_required_settings(self, userid, alias_group, settings_group, channel, new_roles):  # noqa
        """Check if any new setting rows are needed, and prepare them for
        insertion (in order to determine defaults and newly required ticks
        for *other channels* at the very end)
        """
        if settings_group != []:
            for aliased_kind in alias_group:
                if aliased_kind not in [s.kind for s in settings_group]:
                    # This kind (transition ID) doesn't have a row yet
                    # Make sure one gets added with the new roles for
                    # this user, kind and channel
                    self.queue_new_setting_for_insertion(
                        userid, aliased_kind, channel, new_roles)

    def update_existing_settings(self, userid, settings_group, channel, new_roles):  # noqa
        for setting in settings_group:
            old_roles = getattr(setting, channel)
            if set(new_roles) != set(old_roles):
                log.info("Changed: %s - %s - %s" % (
                    userid, channel, setting.kind))
                log.info("  Old roles: %s" % old_roles)
                log.info("  New roles: %s" % new_roles)
            setattr(setting, channel, new_roles)

    def insert_newly_required_settings(self):
        """Based on the list of queued settings to insert, add these new
        setting rows, which respecting defaults.
        """
        to_insert = self.new_settings_to_insert

        for userid in to_insert:
            for aliased_kind in to_insert[userid]:
                log.info(
                    "Adding new setting: %s - %s" % (userid, aliased_kind))
                new_setting = self.create_setting_with_defaults(
                    aliased_kind, userid)

                settings_by_channel = to_insert[userid][aliased_kind]
                for channel in settings_by_channel:
                    new_roles = settings_by_channel[channel]
                    setattr(new_setting, channel, new_roles)
                    log.info("  %s - %s" % (channel, new_roles))
                self.session.add(new_setting)

    def create_setting_with_defaults(self, kind, userid):
        new_setting = NotificationSetting(kind=kind, userid=userid)

        kind_defaults = self.notification_defaults[kind]
        for channel in CHANNELS:
            channel_defaults = getattr(kind_defaults, channel)
            setattr(new_setting, channel, list(channel_defaults))
        return new_setting

    def queue_new_setting_for_insertion(self, userid, aliased_kind, channel, new_roles):  # noqa
        """Queue a new setting row for insertion, by adding the specific
        new_roles that are needed. Other new roles might be needed and
        inserted here for other channels, which is why we don't construct the
        new settings entity immediately, so we can defer its creation to the
        very end, and properly determine defaults vs. actualized values for
        roles.
        """
        to_insert = self.new_settings_to_insert
        if userid not in to_insert:
            to_insert[userid] = {}

        if aliased_kind not in to_insert[userid]:
            to_insert[userid][aliased_kind] = {}

        if channel not in to_insert[userid][aliased_kind]:
            to_insert[userid][aliased_kind][channel] = new_roles
