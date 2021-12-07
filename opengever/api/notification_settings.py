from opengever.activity import notification_center
from opengever.activity.browser.settings import NOTIFICATION_SETTING_TABS
from opengever.activity.browser.settings import USER_SETTINGS
from opengever.activity.model.settings import NotificationDefault
from opengever.activity.notification_settings import NotificationSettings
from opengever.activity.roles import ROLE_TRANSLATIONS
from opengever.api.validation import get_validation_errors
from opengever.meeting import is_meeting_feature_enabled
from opengever.ogds.models.user import User
from opengever.ogds.models.user_settings import UserSettings
from opengever.workspace import is_todo_feature_enabled
from opengever.workspace import is_workspace_feature_enabled
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope import schema
from zope.i18n import translate
from zope.interface import implements
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse


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
            'general': not is_workspace_feature_enabled(),
            'workspace': is_workspace_feature_enabled() and is_todo_feature_enabled(),
            'document': True,
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


class IActivityNotificationSetting(Interface):

    badge = schema.Dict(key_type=schema.TextLine(), value_type=schema.Bool(), required=False)
    digest = schema.Dict(key_type=schema.TextLine(), value_type=schema.Bool(), required=False)
    mail = schema.Dict(key_type=schema.TextLine(), value_type=schema.Bool(), required=False)
    reset = schema.Bool(required=False, default=False)


class IGeneralNotificationSetting(Interface):

    reset = schema.Bool(required=False, default=False)
    value = schema.Bool(required=False, default=False)


class ActivityNotificationSettingHandler(object):
    validation_schema = IActivityNotificationSetting

    def __init__(self):
        self.settings = NotificationSettings()

    def validate_setting_id(self, setting_id):
        if not NotificationDefault.query.by_kind(setting_id).first():
            raise BadRequest("'{}' does not exist".format(setting_id))

    def reset_setting(self, setting_id, userid):
        NotificationSettings().remove_custom_setting(setting_id, userid)

    def update_setting(self, data, setting_id, userid):
        badge_roles = data.get('badge')
        digest_roles = data.get('digest')
        mail_roles = data.get('mail')
        if badge_roles is None and digest_roles is None and mail_roles is None:
            raise BadRequest('Missing parameter badge, digest or mail')
        if badge_roles is not None:
            badge_roles = [key for key, value in badge_roles.items() if value]
        if digest_roles is not None:
            digest_roles = [key for key, value in digest_roles.items() if value]
        if mail_roles is not None:
            mail_roles = [key for key, value in mail_roles.items() if value]

        NotificationSettings().set_custom_setting(setting_id, userid,
                                                  mail_roles=mail_roles,
                                                  badge_roles=badge_roles,
                                                  digest_roles=digest_roles,
                                                  use_default=True)

    def serialize_setting(self, setting_id, userid, url, request):
        group = filter(lambda group: setting_id in group['settings'], NOTIFICATION_SETTING_TABS)[0]
        return serialize_activity_setting(self.settings, setting_id, group, userid, url, request)


class GeneralNotificationSettingHandler(object):
    validation_schema = IGeneralNotificationSetting

    def validate_setting_id(self, setting_id):
        try:
            getattr(UserSettings, setting_id)
        except AttributeError:
            raise BadRequest("'{}' does not exist".format(setting_id))

    def reset_setting(self, setting_id, userid):
        default = getattr(UserSettings, setting_id).default.arg
        UserSettings.save_setting_for_user(userid, setting_id, default)

    def update_setting(self, data, setting_id, userid):
        if data.get('value') is None:
            raise BadRequest('Missing parameter value')
        UserSettings.save_setting_for_user(userid, setting_id, data.get('value'))

    def serialize_setting(self, setting_id, userid, url, request):
        setting = filter(lambda setting: setting.get('id') == setting_id, USER_SETTINGS)[0]
        return serialize_general_setting(setting, userid, url, request)


class NotificationSettingsPatch(Service):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(NotificationSettingsPatch, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@favorites as parameters
        self.params.append(name)
        return self

    def read_params(self):
        if len(self.params) != 2:
            raise BadRequest(
                "Must supply setting category and setting ID as URL path parameters")

        return self.params[0], self.params[1]

    def get_handler(self, setting_category):
        if setting_category == 'general':
            return GeneralNotificationSettingHandler()
        elif setting_category == 'activities':
            return ActivityNotificationSettingHandler()
        raise BadRequest("'{}' does not exist".format(setting_category))

    def validate_data(self, data, schema_interface):
        errors = get_validation_errors(data, schema_interface)
        if errors:
            raise BadRequest(errors)

    def reply(self):
        setting_category, setting_id = self.read_params()
        userid = api.user.get_current().getId()
        user = User.query.filter_by(userid=userid).one_or_none()
        if user is None:
            raise BadRequest("User {} not found in OGDS".format(userid))

        data = json_body(self.request)

        handler = self.get_handler(setting_category)
        self.validate_data(data, handler.validation_schema)
        handler.validate_setting_id(setting_id)
        if data.get('reset'):
            handler.reset_setting(setting_id, userid)
        else:
            handler.update_setting(data, setting_id, userid)

        prefer = self.request.getHeader('Prefer')
        if prefer == 'return=representation':
            url = self.context.absolute_url()
            self.request.response.setStatus(200)
            return handler.serialize_setting(setting_id, userid, url, self.request)

        self.request.response.setStatus(204)
        return None
