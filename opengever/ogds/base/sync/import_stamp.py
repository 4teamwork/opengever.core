from datetime import datetime
from five import grok
from opengever.base.protect import unprotected_write
from opengever.base.request import dispatch_request
from opengever.core import dictstorage
from opengever.ogds.base.interfaces import ISyncStamp
from opengever.ogds.base.utils import ogds_service
from plone import api
from Products.CMFPlone.interfaces import IPloneSiteRoot
from urllib2 import URLError
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.globalrequest import setRequest
import logging


logger = logging.getLogger('opengever.ogds.base')

DICTSTORAGE_SYNC_KEY = 'last_ldap_synchronisation'
REQUEST_SYNC_KEY = 'last_ldap_synchronisation'


def update_sync_stamp(context):
    """update the SYNC key with the actual timestamp in the dictstorage"""

    timestamp = datetime.now().isoformat()
    dictstorage.set(DICTSTORAGE_SYNC_KEY, timestamp)
    logger.info("Updated sync_stamp in dictstorage"
                " to current timestamp (%s)" % timestamp)
    return timestamp


def set_remote_import_stamp(context):
    """update the sync stap on every enabled client."""

    timestamp = update_sync_stamp(context)

    # fake the request, because dispatch_request expects it
    setRequest(context.REQUEST)

    for admin_unit in ogds_service().all_admin_units():
        try:
            dispatch_request(admin_unit.id(), '@@update_sync_stamp',
                             data={REQUEST_SYNC_KEY: timestamp})
            logger.info(
                "Issued remote request to update sync_stamp on %s to %s" % (
                    admin_unit.id(), timestamp))
        except URLError, e:
            logger.warn("ERROR while trying to remotely update sync_stamp"
                        "for %s: %s" % (admin_unit.id(), e))


class SyncStampUtility(grok.GlobalUtility):
    """Named Adapter which handles the persistent storing
    of the LDAP SYNC timestamp"""

    grok.provides(ISyncStamp)

    SYNC_STAMP_KEY = 'sync_stamp'

    def get_context(self, context):
        """helper for get the context, even no context is given."""

        if not context or not IPloneSiteRoot.providedBy(context):
            context = api.portal.get()

        return context

    def get_sync_stamp(self, context=None):
        """return the time stamp from the last Synchronisation."""
        context = self.get_context(context)
        self.annotations = IAnnotations(context)
        return self.annotations.get('sync_stamp')

    def set_sync_stamp(self, stamp, context=None):
        """update the stamp with the given value"""

        context = self.get_context(context)
        self.annotations = unprotected_write(IAnnotations(context))
        self.annotations['sync_stamp'] = stamp
        logger.info("Stored sync_stamp %s in annotations" % stamp)


class UpdateSyncStamp(grok.View):
    """View wich is called from the ogds, after the LDAP Synchronisation"""

    grok.context(IPloneSiteRoot)
    grok.name('update_sync_stamp')
    grok.require('zope2.View')

    INTERN_SYNC_KEY = 'ldap_sync_key'

    def render(self):
        """read the actual timestamp(isoformat) and save it into a annotation.
        """

        timestamp = self.request.form.get(REQUEST_SYNC_KEY, None)

        if timestamp:
            logger.info("Updating sync_stamp to %s" % timestamp)
            getUtility(ISyncStamp).set_sync_stamp(timestamp)
            return True

        return False
