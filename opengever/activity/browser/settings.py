from opengever.activity import _
from opengever.activity import notification_center
from opengever.activity import notification_settings
from opengever.activity.roles import ALWAYS
from opengever.activity.roles import COMMITTEE_RESPONSIBLE_ROLE
from opengever.activity.roles import DISPOSITION_ARCHIVIST_ROLE
from opengever.activity.roles import DISPOSITION_RECORDS_MANAGER_ROLE
from opengever.activity.roles import DOSSIER_RESPONSIBLE_ROLE
from opengever.activity.roles import PROPOSAL_ISSUER_ROLE
from opengever.activity.roles import TASK_ISSUER_ROLE
from opengever.activity.roles import TASK_REMINDER_WATCHER_ROLE
from opengever.activity.roles import TASK_RESPONSIBLE_ROLE
from opengever.activity.roles import TODO_RESPONSIBLE_ROLE
from opengever.activity.roles import WATCHER_ROLE
from opengever.activity.roles import WORKSPACE_MEMBER_ROLE
from opengever.base.handlebars import prepare_handlebars_template
from opengever.base.json_response import JSONResponse
from opengever.meeting import is_meeting_feature_enabled
from opengever.ogds.models.user import User
from opengever.ogds.models.user_settings import UserSettings
from opengever.workspace import is_todo_feature_enabled
from opengever.workspace import is_workspace_feature_enabled
from path import Path
from plone import api
from Products.Five import BrowserView
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate
import json


TEMPLATES_DIR = Path(__file__).joinpath('..', 'templates').abspath()

# The following list contains all necessary informations about the notification
# setting which should be exposed in the notification settings view.
NOTIFICATION_SETTING_TABS = [
    {'id': 'general',
     'roles': [ALWAYS],
     'settings': [
         'added-as-watcher',
         'external-activity',
     ]},

    {'id': 'task',
     'roles': [TASK_ISSUER_ROLE, TASK_RESPONSIBLE_ROLE, WATCHER_ROLE],
     'settings': [
         'task-added-or-reassigned',
         'task-modified',
         'task-commented',
         'task-status-modified'
     ]},

    {'id': 'proposal',
     'roles': [PROPOSAL_ISSUER_ROLE, COMMITTEE_RESPONSIBLE_ROLE],
     'settings': [
         'proposal-transition-submit',
         'proposal-transition-reject',
         'proposal-transition-schedule',
         'proposal-transition-pull',
         'proposal-transition-decide',
         'proposal-commented',
         'proposal-attachment-updated',
         'proposal-additional-documents-submitted',
     ]},

    {'id': 'reminder',
     'roles': [TASK_REMINDER_WATCHER_ROLE],
     'settings': [
         'task-reminder',
     ]},

    {'id': 'disposition',
     'roles': [DISPOSITION_RECORDS_MANAGER_ROLE, DISPOSITION_ARCHIVIST_ROLE],
     'settings': [
         'disposition-added',
         'disposition-transition-appraise',
         'disposition-transition-archive',
         'disposition-transition-close',
         'disposition-transition-dispose',
         'disposition-transition-refuse',
     ]},

    {'id': 'dossier',
     'roles': [DOSSIER_RESPONSIBLE_ROLE],
     'settings': [
         'dossier-overdue',
     ]},

    {'id': 'todos',
     'roles': [TODO_RESPONSIBLE_ROLE, WORKSPACE_MEMBER_ROLE],
     'settings': [
         'todo-assigned',
         'todo-modified'
     ]},
    {'id': 'workspaces',
     'roles': [ALWAYS],
     'settings': [
         'workspace-participation-added'
     ]},
    {'id': 'document',
     'roles': [WATCHER_ROLE],
     'settings': [
         'document-modified',
     ]},
]

USER_SETTINGS = [
    {
        'id': 'notify_own_actions',
        'title': _('notify_own_actions_title',
                   default=u'Enable notifications for own actions'),
        'help_text': _('notify_own_actions_help',
                       default=u'By default no notifications are emitted for a '
                               u'users\'own actions. This option allows to modify '
                               u'this behavior. Notwithstanding this configuration, '
                               u'user notification settings for each action type '
                               u'will get applied anyway.')
    },
    {
        'id': 'notify_inbox_actions',
        'title': _('notify_inbox_actions_title',
                   default=u'Enable notifications for inbox actions'),
        'help_text': _('notify_inbox_actions_help',
                       default=u'Activate, respectively deactivate, all '
                               u'notifications due to your inbox permissions.')
    },
]


class InvalidUser(Exception):
    """User not found in the OGDS.
    """


class NotificationSettingsView(BrowserView):
    """This browserview provides the endpoints for the notification
    settings form.

    There are two type of settings:

    1. User-Settings

    The user settings provides general notification settings for the current user

    2. Notification-Settings

    The notification settings provides notification settings for specific
    activities for the current user.
    """
    def __init__(self, context, request):
        super(NotificationSettingsView, self).__init__(context, request)
        self.settings = notification_settings.NotificationSettings()

    def save_user_setting(self):
        """API function to save a specific user setting.
        """
        try:
            self.assert_user_in_ogds()
        except InvalidUser:
            # User with no entry in the ogds, probably zopemaster.
            msg = "Cannot save configuration for this user as he is not in the ogds"
            return JSONResponse(self.request).error(msg).proceed().dump()

        config_name = self.request.form['config_name']
        value = json.loads(self.request.form['value'])

        UserSettings.save_setting_for_user(
            api.user.get_current().getId(), config_name, value)

        return JSONResponse(self.request).proceed().dump()

    def save_notification_setting(self):
        """API function to save a specific notification setting.
        """
        kind = self.request.form['kind']
        mail = json.loads(self.request.form['mail'])
        badge = json.loads(self.request.form['badge'])
        digest = json.loads(self.request.form['digest'])

        try:
            self.assert_user_in_ogds()
        except InvalidUser:
            # User with no entry in the ogds, probably zopemaster.
            msg = "Cannot save setting for this user as he is not in the ogds"
            return JSONResponse(self.request).error(msg).proceed().dump()

        userid = api.user.get_current().getId()

        self.settings.set_custom_setting(kind, userid,
                                         mail_roles=mail,
                                         badge_roles=badge,
                                         digest_roles=digest)

        return JSONResponse(self.request).proceed().dump()

    def reset_notification_setting(self):
        """API function to reset a notification setting of a specific type.
        """
        kind = self.request.form['kind']

        userid = api.user.get_current().getId()
        self.settings.remove_custom_setting(kind, userid)

        return JSONResponse(self.request).proceed().dump()

    def reset_user_setting(self):
        """API function to reset a user setting of a specific name.
        """
        config_name = self.request.form['config_name']
        default = self.get_default_user_setting_value(config_name)

        UserSettings.save_setting_for_user(
            api.user.get_current().getId(), config_name, default)
        return JSONResponse(self.request).proceed().dump()

    def list(self):
        """API function to get all the required settings for the current user.
        """
        notification_settings = []
        for tab in NOTIFICATION_SETTING_TABS:
            for setting_id in tab.get('settings'):
                config = self.settings.get_configuration_by_id(setting_id)
                kind_title = translate(config.get('title', setting_id), context=self.request)
                item = {'kind_title': kind_title,
                        'edit_mode': True,
                        'kind': setting_id,
                        'type_id': tab.get('id')}

                notification_settings.append(
                    self.add_values(setting_id, item, tab.get('roles')))

        user_settings = []
        for setting in USER_SETTINGS:
            title = translate(setting.get('title'), context=self.request)
            help_text = translate(setting.get('help_text'), context=self.request)

            default = self.get_default_user_setting_value(setting.get('id'))
            value = UserSettings.get_setting_for_user(
                api.user.get_current().getId(), setting.get('id'))

            if value == default:
                setting_type = 'default'
            else:
                setting_type = 'personal'

            user_settings.append({'id': setting.get('id'),
                                  'title': title,
                                  'help_text': help_text,
                                  'value': value,
                                  'setting_type': setting_type
                                  })

        # The mapping here is weird because we refactored the python part but
        # not the Handlebars (JS) part. Because we would have to update a lot
        # of frontend-code, we'll leave it as it is.
        return JSONResponse(self.request).data(
            activities=notification_settings,
            configurations=user_settings,
            translations=self.get_role_translations()).dump()

    def get_role_translations(self):
        roles = {}
        for group in NOTIFICATION_SETTING_TABS:
            for role in group.get('roles'):
                if role in roles:
                    continue

                roles[role] = translate(
                    role, domain='opengever.activity', context=self.request)

        return roles

    def dispatchers(self):
        return notification_center().dispatchers

    def get_default_user_setting_value(self, setting_name):
        return getattr(UserSettings, setting_name).default.arg

    def assert_user_in_ogds(self):
        userid = api.user.get_current().getId()
        user = User.query.filter_by(userid=userid).one_or_none()
        if user is None:
            raise InvalidUser

    def add_values(self, kind, item, roles):
        userid = api.user.get_current().getId()
        setting = self.settings.get_setting(kind, userid)

        is_custom_setting = self.settings.is_custom_setting(setting)
        item['setting_type'] = 'personal' if is_custom_setting else 'default'

        for dispatcher in self.dispatchers():
            values = getattr(setting, dispatcher.roles_key)
            item[dispatcher._id] = {role: bool(role in values) for role in roles}

        return item


class NotificationSettingsForm(BrowserView):
    """Person notification settings form.

    Frontend functionality implemented in setting.js.
    """

    template = ViewPageTemplateFile('templates/settings.pt')

    def __call__(self):
        return self.template()

    def render_form_template(self):
        return prepare_handlebars_template(
            TEMPLATES_DIR.joinpath('settings-form.html'),
            translations=[
                _('label_activity', default=u'Activity'),
                _('label_badge', default=u'Badge'),
                _('label_mail', default=u'Mail'),
                _('label_daily_digest', default=u'Daily Digest'),
                _('btn_save', default=u'Save'),
                _('btn_cancel', default=u'Cancel'),
                _('btn_reset', default=u'Reset')])

    def list_url(self):
        return '{}/notification-settings/list'.format(
            api.portal.get().absolute_url())

    def save_url(self):
        return '{}/notification-settings/save_notification_setting'.format(
            api.portal.get().absolute_url())

    def save_user_setting_url(self):
        return '{}/notification-settings/save_user_setting'.format(
            api.portal.get().absolute_url())

    def reset_url(self):
        return '{}/notification-settings/reset_notification_setting'.format(
            api.portal.get().absolute_url())

    def reset_user_setting_url(self):
        return '{}/notification-settings/reset_user_setting'.format(
            api.portal.get().absolute_url())

    def tab_title_general(self):
        return _('label_general', default=u'General')

    def tab_title_task(self):
        return _('label_tasks', default=u'Tasks')

    def tab_title_proposals(self):
        return _('label_proposals', default=u'Proposals')

    def tab_title_reminders(self):
        return _('label_reminders', default=u'Reminders')

    def tab_title_dispositions(self):
        return _('label_dispositions', default=u'Dispositions')

    def tab_title_dossiers(self):
        return _('label_dossiers', default=u'Dossiers')

    def tab_title_documents(self):
        return _('label_documents', default=u'Documents')

    def tab_title_workspaces(self):
        return _('label_workspaces', default=u'Workspaces')

    def show_disposition_tab(self):
        return api.user.has_permission('opengever.disposition: Add disposition')

    def show_documents_tab(self):
        return True

    def show_proposals_tab(self):
        return is_meeting_feature_enabled()

    def show_workspaces_tab(self):
        return is_workspace_feature_enabled() and is_todo_feature_enabled()
