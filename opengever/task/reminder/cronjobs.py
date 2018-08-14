from opengever.core.debughelpers import get_first_plone_site
from opengever.core.debughelpers import setup_plone
from opengever.task.reminder import logger
from opengever.task.reminder.reminder import get_task_reminder
import logging
import transaction


def generate_remind_notifications_zopectl_handler(app, args):
    stream_handler = logger.root.handlers[0]
    stream_handler.setLevel(logging.INFO)
    logger.setLevel(logging.INFO)

    setup_plone(get_first_plone_site(app))

    logger.info('Start generate remind notifications...')
    created = get_task_reminder().create_reminder_notifications()
    transaction.commit()
    logger.info('Successfully created {} notifications'.format(created))
