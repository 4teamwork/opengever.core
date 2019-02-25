from opengever.core.debughelpers import get_first_plone_site
from opengever.core.debughelpers import setup_plone
from opengever.task.reminder import logger
from opengever.task.reminder.reminder import TaskReminder
from plone import api
import logging
import transaction


def generate_remind_notifications_zopectl_handler(app, args):
    stream_handler = logger.root.handlers[0]
    stream_handler.setLevel(logging.INFO)
    logger.setLevel(logging.INFO)

    plone = setup_plone(get_first_plone_site(app))

    # XXX This should not be necessary, but it seems that language negotiation
    # fails somewhere down the line.
    # Set up the language based on site wide preferred language. We do this
    # so all the i18n and l10n machinery down the line uses the right language.
    lang_tool = api.portal.get_tool('portal_languages')
    lang = lang_tool.getPreferredLanguage()
    plone.REQUEST.environ['HTTP_ACCEPT_LANGUAGE'] = lang
    plone.REQUEST.setupLocale()

    logger.info('Start generate remind notifications...')
    created = TaskReminder().create_reminder_notifications()
    transaction.commit()
    logger.info('Successfully created {} notifications'.format(created))
