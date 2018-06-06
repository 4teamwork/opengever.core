from ftw.upgrade import UpgradeStep
from plone import api


class DropNonWordMeetings(UpgradeStep):
    """Drop non-word meetings feature flag.
    """

    def __call__(self):
        has_meeting_feature = api.portal.get_registry_record(
            'opengever.meeting.interfaces.IMeetingSettings.is_feature_enabled')
        has_word_meeting = api.portal.get_registry_record(
            'opengever.meeting.interfaces.IMeetingSettings.is_word_implementation_enabled')

        if has_meeting_feature:
            assert has_word_meeting, (
                    "Invalid state, must have word meeting to run this "
                    "upgrade. The word meeting should be enabled on a per "
                    "policy base with an upgrade that also migrates content"
            )

        self.install_upgrade_profile()
