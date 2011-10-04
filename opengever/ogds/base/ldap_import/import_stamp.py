from Products.CMFPlone.interfaces import IPloneSiteRoot
from datetime import datetime
from five import grok
from ftw.dictstorage.interfaces import IDictStorage
from opengever.ogds.base.interfaces import IContactInformation, ISyncStamp
from opengever.ogds.base.utils import remote_request
from zope.annotation.interfaces import IAnnotations
from zope.app.component.hooks import getSite
from zope.component import getUtility
from zope.globalrequest import setRequest
from urllib2 import HTTPError


DICTSTORAGE_SYNC_KEY = 'last_ldap_synchronisation'
REQUEST_SYNC_KEY = 'last_ldap_synchronisation'


def update_sync_stamp(context):
    """update the SYNC key with the actual timestamp in the dictstorage"""

    storage = IDictStorage(context)
    timestamp = datetime.now().isoformat()
    storage.set(DICTSTORAGE_SYNC_KEY, timestamp)
    return timestamp


def set_remote_import_stamp(context):
    """update the sync stap on every enabled client."""

    # fake the request, because the remote_request use one
    context = setRequest(context.REQUEST)

    info = getUtility(IContactInformation)
    timestamp = update_sync_stamp(context)
    for client in info.get_clients():
        try:
            remote_request(client.client_id, '@@update_sync_stamp',
                       data={REQUEST_SYNC_KEY: timestamp})
        except HTTPError:
            pass


class SyncStampUtility(grok.GlobalUtility):
    """Named Adapter which handles the persistent storing
    of the LDAP SYNC timestamp"""

    grok.provides(ISyncStamp)

    SYNC_STAMP_KEY = 'sync_stamp'

    def get_context(self, context):
        """helper for get the context, even no context is given."""

        if not context:
            context = getSite()

        # special handling for kks vailidationrequest
        # the context ist set to the Z3CFormValidation object and can't be used
        # so we get the PloneSiteRoot from the aq_chain
        if not IPloneSiteRoot.providedBy(context):
            for obj in context.aq_chain:
                if IPloneSiteRoot.providedBy(obj):
                    context = obj
                    break

        return context

    def get_sync_stamp(self, context=None):
        """return the time stamp from the last Synchronisation."""
        context = self.get_context(context)
        self.annotations = IAnnotations(context)
        return self.annotations.get('sync_stamp')

    def set_sync_stamp(self, stamp, context=None):
        """update the stamp with the given value"""

        context = self.get_context(context)
        self.annotations = IAnnotations(context)
        self.annotations['sync_stamp'] = stamp


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
            getUtility(ISyncStamp).set_sync_stamp(timestamp)
            return True

        return False
