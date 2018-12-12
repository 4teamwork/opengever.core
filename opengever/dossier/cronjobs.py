from opengever.core.debughelpers import all_plone_sites
from opengever.core.debughelpers import setup_plone
from opengever.dossier.activities import DossierOverdueActivityGenerator
import logging
import transaction


logger = logging.getLogger('opengever.dossier.cronjobs')


def generate_overdue_notifications_zopectl_handler(app, args):
    # Set Zope's default StreamHandler's level to INFO (default is WARNING)
    # to make sure send_digests()'s output gets logged on console
    stream_handler = logger.root.handlers[0]
    stream_handler.setLevel(logging.INFO)
    logger.setLevel(logging.INFO)

    for plone_site in all_plone_sites(app):
        setup_plone(plone_site)
        created = DossierOverdueActivityGenerator()()
        logger.info('Successfully created {} notifications'.format(created))

        transaction.commit()
