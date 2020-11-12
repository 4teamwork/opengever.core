from opengever.activity import notification_center
from opengever.activity.browser.settings import NOTIFICATION_SETTING_TABS
from opengever.activity.browser.settings import USER_SETTINGS
from opengever.activity.notification_settings import NotificationSettings
from opengever.activity.roles import ROLE_TRANSLATIONS
from opengever.meeting import is_meeting_feature_enabled
from opengever.ogds.models.user_settings import UserSettings
from opengever.workspace import is_workspace_feature_enabled
from plone import api
from plone.restapi.services import Service
from zope.i18n import translate


def serialize_activity_setting(settings, kind, group, userid, url, request):
    config = settings.get_configuration_by_id(kind)
    setting = settings.get_setting(kind, userid)
    item = {
        '@id': '{}/@notification-settings/activities/{}'.format(url, kind),
        'id': kind,
        'kind': kind,
        'group': group['id'],
        'personal': settings.is_custom_setting(setting),
        'title': translate(config['title'], domain='opengever.activity',
                           context=request)
    }

    for dispatcher in notification_center().dispatchers:
        values = getattr(setting, dispatcher.roles_key)
        item[dispatcher._id] = {role: bool(role in values) for role in group['roles']}
    return item


def serialize_general_setting(setting, userid, url, request):
    default = getattr(UserSettings, setting['id']).default.arg
    value = UserSettings.get_setting_for_user(userid, setting.get('id'))
    return {
        '@id': '{}/@notification-settings/general/{}'.format(url, setting['id']),
        'id': setting['id'],
        'value': value,
        'group': 'general',
        'personal': value != default,
        'title': translate(setting['title'], domain='opengever.activity', context=request),
        'help_text': translate(setting['help_text'], domain='opengever.activity',
                               context=request)
    }


class NotificationSettingsGet(Service):

    def group_visibility(self):
        return {
            'disposition': api.user.has_permission('opengever.disposition: Add disposition'),
            'dossier': not is_workspace_feature_enabled(),
            'proposal': is_meeting_feature_enabled(),
            'reminder': not is_workspace_feature_enabled(),
            'task': not is_workspace_feature_enabled(),
            'watcher': not is_workspace_feature_enabled(),
            'workspace': is_workspace_feature_enabled(),
        }

    def general_settings_visibility(self):
        return {
            'notify_own_actions': True,
            'notify_inbox_actions': not is_workspace_feature_enabled()
        }

    def reply(self):
        group_visibility = self.group_visibility()
        general_settings_visibility = self.general_settings_visibility()
        roles = set()
        settings = NotificationSettings()
        userid = api.user.get_current().getId()
        url = self.context.absolute_url()

        activities = {'@id': '{}/@notification-settings/activities'.format(url),
                      'items': []}
        for group in NOTIFICATION_SETTING_TABS:
            if not group_visibility[group['id']]:
                continue
            roles.update(group['roles'])
            for kind in group['settings']:
                activities['items'].append(
                    serialize_activity_setting(settings, kind, group, userid, url, self.request))

        general = {'@id': '{}/@notification-settings/general'.format(url),
                   'items': []}
        for setting in USER_SETTINGS:
            if not general_settings_visibility[setting['id']]:
                continue
            general['items'].append(serialize_general_setting(setting, userid, url, self.request))

        return {'@id': '{}/@notification-settings'.format(url),
                'activities': activities, 'general': general,
                'translations': [{'id': role, 'title': translate(
                    ROLE_TRANSLATIONS[role], context=self.request)} for role in roles]}
