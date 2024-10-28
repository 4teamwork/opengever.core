from AccessControl.SecurityManagement import newSecurityManager
from opengever.core.debughelpers import get_first_plone_site
from opengever.core.debughelpers import setup_plone
from opengever.ogds.base.sync.ogds_updater import sync_ogds
from opengever.workspace import is_workspace_feature_enabled
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

    # Switch security context to 'zopemaster' instead of SpecialUsers.system.
    # This is required because in multi-tenant setups, the OGDS sync will
    # dispatch a remote request to update the sync timestamp. This request
    # will need to be authenticated and therefore needs a user which has an
    # actual userid - which the SpecialUsers.system doesn't.
    user = app.acl_users.getUser('zopemaster')
    user = user.__of__(app.acl_users)
    newSecurityManager(app, user)

    sync_ogds(plone, local_groups=is_workspace_feature_enabled())
    transaction.commit()
