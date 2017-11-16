from opengever.activity.badge import BadgeIconDispatcher
from opengever.activity.center import DisabledNotificationCenter
from opengever.activity.center import PloneNotificationCenter
from opengever.activity.interfaces import IActivitySettings
from opengever.activity.mail import PloneNotificationMailer
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface


_ = MessageFactory("opengever.activity")


def is_activity_feature_enabled():
    try:
        registry = getUtility(IRegistry)
        return registry.forInterface(IActivitySettings).is_feature_enabled

    except KeyError, AttributeError:
        return False


def notification_center():
    if not is_activity_feature_enabled():
        return DisabledNotificationCenter()

    return PloneNotificationCenter(
        dispatchers=[PloneNotificationMailer(), BadgeIconDispatcher()])


ACTIVITY_TRANSLATIONS = {
    'task-added': _('task-added', default=u'Task added'),
    'task-transition-cancelled-open': _(
        'task-transition-cancelled-open', default=u'Task reopend'),
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
        'task-transition-resolved-in-progress', default=u'Task revision wanted'),
    'task-transition-resolved-tested-and-closed': _(
        'task-transition-resolved-tested-and-closed', default=u'Task closed'),
    'forwarding-added':_(
        'forwarding-added', default=u'Forwarding added'),
    'forwarding-transition-accept': _(
        'forwarding-transition-accept', default=u'Forwarding accepted'),
    'forwarding-transition-assign-to-dossier': _(
        'forwarding-transition-assign-to-dossier',
        default=u'Forwarding assigned to dossier'),
    'forwarding-transition-close': _('forwarding-transition-close', default=u'Forwarding closed'),
    'forwarding-transition-reassign': _(
        'forwarding-transition-reassign', default=u'Forwarding reassigned'),
    'forwarding-transition-reassign-refused': _(
        'forwarding-transition-reassign-refused',
        default=u'Forwarding reassigned and refused'),
    'forwarding-transition-refuse': _(
        'forwarding-transition-refuse', default=u'Forwarding refused')
}
