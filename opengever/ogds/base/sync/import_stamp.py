from datetime import datetime
from opengever.base.protect import unprotected_write
from opengever.base.request import dispatch_request
from opengever.base.request import tracebackify
from opengever.core import dictstorage
from opengever.ogds.base.interfaces import ISyncStamp
from opengever.ogds.models.service import ogds_service
from plone import api
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser import BrowserView
from urllib2 import URLError
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.globalrequest import setRequest
from zope.interface import implementer
import logging


logger = logging.getLogger('opengever.ogds.base')

DICTSTORAGE_SYNC_KEY = 'last_ldap_synchronisation'
REQUEST_SYNC_KEY = 'last_ldap_synchronisation'


def update_sync_stamp(context):
    """Update the sync stamp with the current timestamp in the dictstorage.
    """
    timestamp = datetime.now().isoformat()
    dictstorage.set(DICTSTORAGE_SYNC_KEY, timestamp)
    logger.info("Updated sync_stamp in dictstorage"
                " to current timestamp (%s)" % timestamp)
    return timestamp


def set_remote_import_stamp(context):
    """Update the sync stamp on every enabled admin unit.
    """
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


@implementer(ISyncStamp)
class SyncStampUtility(object):
    """Global utility that handles persistent storage of the LDAP sync stamp.
    """

    SYNC_STAMP_KEY = 'sync_stamp'

    def get_context(self, context):
        """Helper to get the context, even if no context is given.
        """
        if not context or not IPloneSiteRoot.providedBy(context):
            context = api.portal.get()

        return context

    def get_sync_stamp(self, context=None):
        """Return the sync stamp (time stamp of last LDAP synchronisation).
        """
        context = self.get_context(context)
        self.annotations = IAnnotations(context)
        return self.annotations.get('sync_stamp')

    def set_sync_stamp(self, stamp, context=None):
        """Update sync stamp with the given value.
        """
        context = self.get_context(context)
        self.annotations = unprotected_write(IAnnotations(context))
        self.annotations['sync_stamp'] = stamp
        logger.info("Stored sync_stamp %s in annotations" % stamp)


@tracebackify
class UpdateSyncStamp(BrowserView):
    """View to update local sync stamp (used in cache keys).

    This view is called from OGDS (possibly from a remote admin unit), after
    performing LDAP Synchronisation.
    """

    INTERN_SYNC_KEY = 'ldap_sync_key'

    def __call__(self):
        """Read timestamp (isoformat) from request and set as local sync stamp.
        """
        timestamp = self.request.form.get(REQUEST_SYNC_KEY, None)

        if timestamp:
            logger.info("Updating sync_stamp to %s" % timestamp)
            getUtility(ISyncStamp).set_sync_stamp(timestamp)
            return True

        return False
