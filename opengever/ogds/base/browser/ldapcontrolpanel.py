from five import grok
from logging import StreamHandler
from opengever.core import dictstorage
from opengever.ogds.base.interfaces import ISyncStamp
from opengever.ogds.base.sync.import_stamp import DICTSTORAGE_SYNC_KEY
from opengever.ogds.base.sync.import_stamp import set_remote_import_stamp
from opengever.ogds.base.sync.ogds_updater import LOG_FORMAT
from opengever.ogds.base.sync.ogds_updater import sync_ogds
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getUtility
import logging


class LDAPControlPanel(grok.View):
    """Displays infos and links about and for the ldap synchronisation
    """

    grok.name('ldap_controlpanel')
    grok.context(IPloneSiteRoot)
    grok.require('cmf.ManagePortal')

    def get_local_sync_stamp(self):
        """Return the current local sync stamp
        which is used by the different cachekeys"""

        return getUtility(ISyncStamp).get_sync_stamp()

    def get_db_sync_stamp(self):
        timestamp = dictstorage.get(DICTSTORAGE_SYNC_KEY)
        return timestamp


class LDAPSyncView(grok.View):
    """Base class for LDAP synchronization views (UserSyncView and
    GroupSyncView).
    """

    grok.context(IPloneSiteRoot)
    grok.require('cmf.ManagePortal')

    def run_update(self, **kwargs):
        # Set up logging to HTTPResponse
        response = BytestringEnforcingResponseWrapper(self.request.RESPONSE)
        logger = logging.getLogger('opengever.ogds.base')
        response_handler = StreamHandler(stream=response)
        response_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(response_handler)

        try:
            sync_ogds(self.context, **kwargs)
        finally:
            # Make sure to remove response logging handler because handlers
            # live for the duration of the Python process, but responses
            # are short-lived
            logger.removeHandler(response_handler)

    def render(self):
        raise NotImplementedError


class UserSyncView(LDAPSyncView):
    """Browser view that starts an LDAP user import.
    """

    grok.name('sync_users')

    def render(self):
        self.run_update(groups=False)


class GroupSyncView(LDAPSyncView):
    """Browser view that starts an LDAP group import.
    """

    grok.name('sync_groups')

    def render(self):
        self.run_update(users=False)


class ResetStampView(grok.View):
    """A view wich reset the actual syncstamp with a actual stamp
    on every client registered in the ogds """

    grok.name('reset_syncstamp')
    grok.context(IPloneSiteRoot)
    grok.require('cmf.ManagePortal')

    def render(self):
        set_remote_import_stamp(self.context)
        IStatusMessage(self.context.REQUEST).addStatusMessage(
            u"Successfully reset the Syncstamp on every client", "info")

        url = self.context.REQUEST.environ.get('HTTP_REFERER')
        if not url:
            url = self.context.absolute_url()

        return self.context.REQUEST.RESPONSE.redirect(url)


class BytestringEnforcingResponseWrapper(object):
    """Because the Zope HTTPResponse.write() method does not accept unicode
    (only byte strings) and raises a ValueError if unicode is passed in, we
    need to wrap it to make sure to convert anything that gets logged from
    somewhere is enforced to be an UTF-8 encoded bytestring.
    """

    def __init__(self, response):
        self.response = response

    def enforce_utf8(self, data):
        if isinstance(data, unicode):
            data = data.encode('utf-8')
        return data

    def write(self, data):
        return self.response.write(self.enforce_utf8(data))
