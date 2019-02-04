from opengever.activity import _
from opengever.activity import ACTIVITIES_ICONS
from opengever.activity import ACTIVITY_TRANSLATIONS
from opengever.activity import notification_center
from opengever.activity.model.settings import NotificationDefault
from opengever.activity.model.settings import NotificationSetting
from opengever.activity.roles import COMMITTEE_RESPONSIBLE_ROLE
from opengever.activity.roles import DISPOSITION_ARCHIVIST_ROLE
from opengever.activity.roles import DISPOSITION_RECORDS_MANAGER_ROLE
from opengever.activity.roles import DOSSIER_RESPONSIBLE_ROLE
from opengever.activity.roles import PROPOSAL_ISSUER_ROLE
from opengever.activity.roles import TASK_ISSUER_ROLE
from opengever.activity.roles import TASK_REMINDER_WATCHER_ROLE
from opengever.activity.roles import TASK_RESPONSIBLE_ROLE
from opengever.base.handlebars import prepare_handlebars_template
from opengever.base.model import create_session
from opengever.base.response import JSONResponse
from opengever.meeting import is_meeting_feature_enabled
from opengever.task.response_description import ResponseDescription
from path import Path
from plone import api
from Products.Five import BrowserView
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate
import json


TEMPLATES_DIR = Path(__file__).joinpath('..', 'templates').abspath()


# The following list contains all necessary informations about the activity
# groups which should be exposed in the notification settings form.
ACTIVITY_GROUPS = [
    {'id': 'task',
     'roles': [TASK_ISSUER_ROLE, TASK_RESPONSIBLE_ROLE],
     'activities': [
         'task-added',
         'task-transition-cancelled-open',
         'task-transition-delegate',
         'task-transition-in-progress-resolved',
         'task-transition-in-progress-tested-and-closed',
         'task-transition-modify-deadline',
         'task-transition-open-cancelled',
         'task-transition-open-in-progress',
         'task-transition-open-rejected',
         'task-commented',
         'task-transition-reassign',
         'task-transition-resolved-in-progress',
         'task-transition-rejected-skipped',
     ]},

    {'id': 'forwarding',
     'roles': [TASK_ISSUER_ROLE, TASK_RESPONSIBLE_ROLE],
     'activities': [
         'forwarding-added',
         'forwarding-transition-accept',
         'forwarding-transition-assign-to-dossier',
         'forwarding-transition-close',
         'forwarding-transition-reassign',
         'forwarding-transition-reassign-refused',
         'forwarding-transition-refuse'
     ]},

    {'id': 'proposal',
     'roles': [PROPOSAL_ISSUER_ROLE, COMMITTEE_RESPONSIBLE_ROLE],
     'activities': [
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
     'activities': [
         'task-reminder',
     ]},

    {'id': 'disposition',
     'roles': [DISPOSITION_RECORDS_MANAGER_ROLE, DISPOSITION_ARCHIVIST_ROLE],
     'activities': [
         'disposition-added',
         'disposition-transition-appraise',
         'disposition-transition-archive',
         'disposition-transition-close',
         'disposition-transition-dispose',
         'disposition-transition-refuse',
     ]},

    {'id': 'dossier',
     'roles': [DOSSIER_RESPONSIBLE_ROLE],
     'activities': [
         'dossier-overdue',
     ]},
]


ALIASES = {
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
        'task-transition-skipped-open',
    ),
    'task-transition-rejected-skipped': (
        'task-transition-rejected-skipped',
        'task-transition-planned-skipped',
    ),
    'disposition-transition-close': (
        'disposition-transition-close',
        'disposition-transition-appraised-to-closed',
    )
}


class NotificationSettings(BrowserView):
    """Settings-form endpoints.
    """

    user_settings = None
    defaults = None

    def save(self):
        """Save setting change
        """
        kind = self.request.form['kind']
        mail = json.loads(self.request.form['mail'])
        badge = json.loads(self.request.form['badge'])
        digest = json.loads(self.request.form['digest'])

        if ALIASES.get(kind):
            kinds = ALIASES.get(kind)
        else:
            kinds = (kind, )

        for kind in kinds:
            setting = self.get_or_create_setting(kind)
            setting.mail_notification_roles = mail
            setting.badge_notification_roles = badge
            setting.digest_notification_roles = digest

        return JSONResponse(self.request).proceed().dump()

    def reset(self):
        """Reset a personal setting
        """
        kind = self.request.form['kind']

        if ALIASES.get(kind):
            kinds = ALIASES.get(kind)
        else:
            kinds = (kind, )

        for kind in kinds:
            setting = self.get_setting(kind)
            create_session().delete(setting)

        return JSONResponse(self.request).proceed().dump()

    def list(self):
        """Returns settings for the current user.
        """
        activities = []
        for group in ACTIVITY_GROUPS:
            for kind in group.get('activities'):
                kind_title = translate(
                    ACTIVITY_TRANSLATIONS[kind], context=self.request)

                item = {'kind_title': kind_title,
                        'edit_mode': True,
                        'css_class': self._get_activity_class(kind),
                        'kind': kind,
                        'type_id': group.get('id')}

                activities.append(
                    self.add_values(kind, item, group.get('roles')))

        return JSONResponse(self.request).data(
            activities=activities,
            translations=self.get_role_translations()).dump()

    def get_role_translations(self):
        roles = {}
        for group in ACTIVITY_GROUPS:
            for role in group.get('roles'):
                if role in roles:
                    continue

                roles[role] = translate(
                    role, domain='opengever.activity', context=self.request)

        return roles

    def dispatchers(self):
        return notification_center().dispatchers

    def get_user_settings(self):
        userid = api.user.get_current().getId()
        if not self.user_settings:
            self.user_settings = {
                setting.kind: setting for setting
                in NotificationSetting.query.filter_by(userid=userid)}

        return self.user_settings

    def get_defaults(self):
        if not self.defaults:
            self.defaults = {default.kind: default
                             for default in NotificationDefault.query}

        return self.defaults

    def get_setting(self, kind):
        userid = api.user.get_current().getId()
        return NotificationSetting.query.filter_by(
            userid=userid, kind=kind).first()

    def get_or_create_setting(self, kind):
        setting = self.get_setting(kind)
        if not setting:
            setting = NotificationSetting(
                kind=kind, userid=api.user.get_current().getId())
            create_session().add(setting)

        return setting

    def add_values(self, kind, item, roles):
        setting = self.get_user_settings().get(kind)

        if not setting:
            item['setting_type'] = 'default'
            setting = self.get_defaults()[kind]
        else:
            item['setting_type'] = 'personal'

        for dispatcher in self.dispatchers():
            values = getattr(setting, dispatcher.roles_key)
            item[dispatcher._id] = {role: bool(role in values) for role in roles}

        return item

    def _get_activity_class(self, kind):
        css_class = ACTIVITIES_ICONS.get(kind)
        if not css_class:
            css_class = ResponseDescription.get(transition=kind).css_class
        return css_class


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
        return '{}/notification-settings/save'.format(
            api.portal.get().absolute_url())

    def reset_url(self):
        return '{}/notification-settings/reset'.format(
            api.portal.get().absolute_url())

    def tab_title_task(self):
        return _('label_tasks', default=u'Tasks')

    def tab_title_forwardings(self):
        return _('label_forwardings', default=u'Forwardings')

    def tab_title_proposals(self):
        return _('label_proposals', default=u'Proposals')

    def tab_title_reminders(self):
        return _('label_reminders', default=u'Reminders')

    def tab_title_dispositions(self):
        return _('label_dispositions', default=u'Dispositions')

    def tab_title_dossiers(self):
        return _('label_dossiers', default=u'Dossiers')

    def show_disposition_tab(self):
        return api.user.has_permission('opengever.disposition: Add disposition')

    def show_proposals_tab(self):
        return is_meeting_feature_enabled()
