from opengever.activity import _
from opengever.activity import ACTIVITY_TRANSLATIONS
from opengever.activity import notification_center
from opengever.activity.model.settings import NotificationDefault
from opengever.activity.model.settings import NotificationSetting
from opengever.activity.roles import TASK_ISSUER_ROLE
from opengever.activity.roles import TASK_RESPONSIBLE_ROLE
from opengever.base.handlebars import prepare_handlebars_template
from opengever.base.model import create_session
from opengever.base.response import JSONResponse
from opengever.task.response_description import ResponseDescription
from path import Path
from plone import api
from Products.Five import BrowserView
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
         'task-transition-open-resolved',
         'task-transition-open-tested-and-closed',
         'task-commented',
         'task-transition-reassign',
         'task-transition-rejected-open',
         'task-transition-resolved-in-progress',
         'task-transition-resolved-tested-and-closed'
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
         'forwarding-transition-refuse']
     }
]


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

        # todo check roles before save
        setting = self.get_or_create_setting(kind)
        setting.mail_notification_roles = mail
        setting.badge_notification_roles = badge

        return JSONResponse(self.request).proceed().dump()

    def reset(self):
        """Reset a personal setting
        """
        kind = self.request.form['kind']
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
                        'css_class': ResponseDescription.get(transition=kind).css_class,
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


class NotificationSettingsForm(BrowserView):
    """Person notification settings form.

    Frontend functionality implemented in setting.js.
    """

    def render_form_template(self):
        return prepare_handlebars_template(
            TEMPLATES_DIR.joinpath('settings-form.html'),
            translations=[
                _('label_activity', default=u'Activity'),
                _('label_badge', default=u'Badge'),
                _('label_mail', default=u'Mail'),
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
