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
    'task-reminder': _(
        'task-reminder', default=u'Task reminder'),
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
    'document-author-changed': _(
        'document-author-changed',
        default=u'Document author changed'),
    'document-title-changed': _(
        'document-title-changed',
        default=u'Document title changed'),
    'document-version-created': _(
        'document-version-created',
        default=u'New document version created'),
}
