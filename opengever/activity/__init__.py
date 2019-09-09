from opengever.activity.badge import BadgeIconDispatcher
from opengever.activity.center import DisabledNotificationCenter
from opengever.activity.center import NotificationCenter
from opengever.activity.center import PloneNotificationCenter
from opengever.activity.digest import DigestDispatcher
from opengever.activity.digest import DigestMailer
from opengever.activity.interfaces import IActivitySettings
from opengever.activity.mail import PloneNotificationMailer
from opengever.core.debughelpers import get_first_plone_site
from opengever.core.debughelpers import setup_plone
from opengever.ogds.base.actor import SYSTEM_ACTOR_ID
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory
import logging
import transaction


logger = logging.getLogger('opengever.activity')


_ = MessageFactory("opengever.activity")


def is_activity_feature_enabled():
    try:
        registry = getUtility(IRegistry)
        return registry.forInterface(IActivitySettings).is_feature_enabled

    except (KeyError, AttributeError):
        return False


def notification_center():
    return _notification_center(PloneNotificationCenter)


def base_notification_center():
    return _notification_center(NotificationCenter)


def _notification_center(cls):
    if not is_activity_feature_enabled():
        return DisabledNotificationCenter()

    return cls(dispatchers=[
        PloneNotificationMailer(), BadgeIconDispatcher(), DigestDispatcher()])


def send_digest_zopectl_handler(app, args):
    # Set Zope's default StreamHandler's level to INFO (default is WARNING)
    # to make sure send_digests()'s output gets logged on console
    stream_handler = logger.root.handlers[0]
    stream_handler.setLevel(logging.INFO)

    plone = setup_plone(get_first_plone_site(app))

    # XXX This should not be necessary, but it seems that language negotiation
    # fails somewhere down the line.
    # Set up the language based on site wide preferred language. We do this
    # so all the i18n and l10n machinery down the line uses the right language.
    lang_tool = api.portal.get_tool('portal_languages')
    lang = lang_tool.getPreferredLanguage()
    plone.REQUEST.environ['HTTP_ACCEPT_LANGUAGE'] = lang
    plone.REQUEST.setupLocale()

    DigestMailer().send_digests()
    transaction.commit()


ACTIVITY_TRANSLATIONS = {
    'task-added': _('task-added', default=u'Task added'),
    'task-transition-cancelled-open': _(
        'task-transition-cancelled-open', default=u'Task reopened'),
    'task-transition-delegate': _(
        'task-transition-delegate', default=u'Task delegated'),
    'task-transition-in-progress-resolved': _(
        'task-transition-in-progress-resolved', default=u'Task resolved'),
    'task-transition-in-progress-tested-and-closed': _(
        'task-transition-in-progress-tested-and-closed',
        default=u'Task closed'),
    'task-transition-modify-deadline': _(
        'task-transition-modify-deadline', default=u'Task deadline modified'),
    'task-transition-open-cancelled': _(
        'task-transition-open-cancelled', default=u'Task cancelled'),
    'task-transition-open-in-progress': _(
        'task-transition-open-in-progress', default=u'Task accepted'),
    'task-transition-open-rejected': _(
        'task-transition-open-rejected', default=u'Task rejected'),
    'task-transition-open-resolved': _(
        'task-transition-open-resolved', default=u'Task resolved'),
    'task-transition-open-tested-and-closed': _(
        'task-transition-open-tested-and-closed', default=u'Task closed'),
    'task-commented': _('task-commented', default=u'Task commented'),
    'task-transition-reassign': _(
        'task-transition-reassign', default=u'Task reassign'),
    'task-transition-rejected-open': _(
        'task-transition-rejected-open', default=u'Task reopened'),
    'task-transition-resolved-in-progress': _(
        'task-transition-resolved-in-progress', default=u'Task revision wanted'),  # noqa
    'task-transition-resolved-tested-and-closed': _(
        'task-transition-resolved-tested-and-closed', default=u'Task closed'),
    'task-transition-skipped-open': _(
        'task-transition-skipped-open', default=u'Task reopened'),
    'task-transition-rejected-skipped': _(
        'task-transition-rejected-skipped', default=u'Task skipped'),
    'task-transition-planned-skipped': _(
        'task-transition-planned-skipped', default=u'Task skipped'),
    'task-reminder': _(
        'task-reminder', default=u'Task reminder'),
    'transition-add-subtask': _('transition-add-subtask', 'Subtask added'),
    'transition-add-document': _('transition-add-document', 'Document added'),
    'forwarding-added': _(
        'forwarding-added', default=u'Forwarding added'),
    'forwarding-transition-accept': _(
        'forwarding-transition-accept', default=u'Forwarding accepted'),
    'forwarding-transition-assign-to-dossier': _(
        'forwarding-transition-assign-to-dossier',
        default=u'Forwarding assigned to dossier'),
    'forwarding-transition-close': _('forwarding-transition-close', default=u'Forwarding closed'),  # noqa
    'forwarding-transition-reassign': _(
        'forwarding-transition-reassign', default=u'Forwarding reassigned'),
    'forwarding-transition-reassign-refused': _(
        'forwarding-transition-reassign-refused',
        default=u'Forwarding reassigned and refused'),
    'forwarding-transition-refuse': _(
        'forwarding-transition-refuse', default=u'Forwarding refused'),
    'proposal-transition-reject': _(
        'proposal-transition-reject', default=u'Proposal rejected'),
    'proposal-transition-schedule': _(
        'proposal-transition-schedule', default=u'Proposal scheduled'),
    'proposal-transition-pull': _(
        'proposal-transition-pull', default=u'Proposal pulled'),
    'proposal-transition-decide': _(
        'proposal-transition-decide', default=u'Proposal decided'),
    'proposal-transition-submit': _(
        'proposal-transition-submit', default=u'Proposal submitted'),
    'proposal-commented': _('proposal-commented', default=u'Proposal commented'),
    'proposal-attachment-updated': _('proposal-attachment-updated',
                                     default=u'Attachment updated'),
    'proposal-additional-documents-submitted': _(
        'proposal-additional-documents-submitted',
        default=u'Additional documents submitted'),
    'submitted-proposal-commented': _(
        'submitted-proposal-commented',
        default=u'Submitted proposal commented'),
    'disposition-added': _(
        'disposition-added',
        default=u'Disposition added'),
    'disposition-transition-appraise': _(
        'disposition-transition-appraise',
        default=u'Disposition appraised'),
    'disposition-transition-archive': _(
        'disposition-transition-archive',
        default=u'Disposition archived'),
    'disposition-transition-dispose': _(
        'disposition-transition-dispose',
        default=u'Disposition disposed'),
    'disposition-transition-refuse': _(
        'disposition-transition-refuse',
        default=u'Disposition refused'),
    'disposition-transition-close': _(
        'disposition-transition-close',
        default=u'Disposition closed'),
    'dossier-overdue': _(
        'dossier-overdue',
        default=u'Overdue dossier'),
    'todo-assigned': _(
        'todo-assigned',
        default=u'ToDo assigned'),
    'todo-modified': _(
        'todo-modified',
        default=u'ToDo modified'),
    'notify_own_actions': {
        'title': _('notify_own_actions_title',
                   default=u'Enable notifications for own actions'),
        'help_text': _('notify_own_actions_help',
                   default=u'By default no notifications are emitted for a '
                            'users\'own actions. This option allows to modify '
                            'this behavior. Notwithstanding this configuration, '
                            'user notification settings for each action type '
                            'will get applied anyway.')
         },
    'notify_inbox_actions': {
        'title': _('notify_inbox_actions_title',
                   default=u'Enable notifications for inbox actions'),
        'help_text': _('notify_inbox_actions_help',
                   default=u'Activate, respectively deactivate, all '
                            'notifications due to your inbox permissions.')
         }
}

# TODO: There are too many places where the activites are defined:
# - ACTIVITE_TRANSLATIONS
# - ACTIVITE_ICONS
# - activity/hooks.py
# - activity/browser/settings.py
# - opengever/task/response_description.py
#
# All the necessary information about an activity should be defined in one place
# and should be used everywhere.
#
# i.e. ACTIVITIES = {
#     'task-added': {
#         'id': 'task-added',
#         'css_class': 'created',
#         'translation': _('task-added'),
#         'category': 'task'
#     }
# }
#
ACTIVITIES_ICONS = {
    'proposal-transition-reject': 'rejected',
    'proposal-transition-schedule': 'scheduled',
    'proposal-transition-pull': 'pulled',
    'proposal-transition-decide': 'decided',
    'proposal-transition-submit': 'submitted',
    'proposal-commented': 'commented',
    'proposal-attachment-updated': 'documentUpdated',
    'proposal-additional-documents-submitted': 'documentAdded',
    'task-reminder': 'taskReminder',
    'disposition-added': 'created',
    'disposition-transition-appraise': 'dispositionAppraised',
    'disposition-transition-archive': 'dispositionArchived',
    'disposition-transition-dispose': 'dispositionDisposed',
    'disposition-transition-refuse': 'dispositionRefused',
    'disposition-transition-close': 'dispositionClosed',
    'dossier-overdue': 'dossierOverdue',
}
