from opengever.core.debughelpers import all_plone_sites
from opengever.core.debughelpers import setup_plone
from opengever.dossier.activities import DossierOverdueActivityGenerator
from plone import api
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
        plone = setup_plone(plone_site)

        # XXX This should not be necessary, but it seems that language negotiation
        # fails somewhere down the line.
        # Set up the language based on site wide preferred language. We do this
        # so all the i18n and l10n machinery down the line uses the right language.
        lang_tool = api.portal.get_tool('portal_languages')
        lang = lang_tool.getPreferredLanguage()
        plone.REQUEST.environ['HTTP_ACCEPT_LANGUAGE'] = lang
        plone.REQUEST.setupLocale()

        created = DossierOverdueActivityGenerator()()
        logger.info('Successfully created {} notifications'.format(created))

        transaction.commit()
