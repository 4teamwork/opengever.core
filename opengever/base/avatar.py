from ftw.avatar.default import DefaultAvatarGenerator
from opengever.base.interfaces import IGeverUI
from plone import api


class GeverDefaultAvatarGenerator(DefaultAvatarGenerator):
    """Customization of ftw.avatars Default generator, which checks the
    UI feature flag and only generates a fallback when flag is enabled."""

    def generate(self, userid, output_stream):
        if not api.portal.get_registry_record(
                'is_feature_enabled', interface=IGeverUI):
            return False

        return super(GeverDefaultAvatarGenerator, self).generate(
            userid, output_stream)
