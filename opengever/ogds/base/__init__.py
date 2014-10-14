from opengever.core.debughelpers import get_first_plone_site
from opengever.core.debughelpers import setup_plone
from opengever.ogds.base.sync.ogds_updater import sync_ogds
from zope.i18nmessageid import MessageFactory
import logging
import transaction


logger = logging.getLogger('opengever.ogds.base')
_ = MessageFactory('opengever.ogds.base')


def sync_ogds_zopectl_handler(app, args):
    # Set Zope's default StreamHandler's level to INFO (default is WARNING)
    # to make sure sync_ogds()'s output gets logged on console
    stream_handler = logger.root.handlers[0]
    stream_handler.setLevel(logging.INFO)

    plone = setup_plone(get_first_plone_site(app))
    sync_ogds(plone)
    transaction.commit()
