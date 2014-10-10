from five import grok
from opengever.core import dictstorage
from opengever.ogds.base.interfaces import IOGDSUpdater
from opengever.ogds.base.interfaces import ISyncStamp
from opengever.ogds.base.sync.import_stamp import DICTSTORAGE_SYNC_KEY
from opengever.ogds.base.sync.import_stamp import set_remote_import_stamp
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from time import strftime
from zope.component import getUtility
import time
import transaction


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

    def mklog(self):
        """Helper to prepend a time stamp to the output.
        """
        write = self.request.RESPONSE.write

        def log(msg, timestamp=True):
            if timestamp:
                msg = '%s : %s \n' % (strftime('%Y/%m/%d-%H:%M:%S '), msg)
            write(msg)
        return log

    def run_update(self):
        raise NotImplemented

    def render(self):
        self.log = self.mklog()

        # Run import and time it
        now = time.clock()
        self.run_update()
        transaction.commit()
        elapsed = time.clock() - now
        self.log("Done in %.0f seconds." % elapsed)

        # Update import time stamp and finally commit
        self.log("Updating LDAP SYNC importstamp...")
        set_remote_import_stamp(self.context)
        self.log("Committing transaction...")
        transaction.commit()
        self.log('Done.')


class UserSyncView(LDAPSyncView):
    """Browser view that starts an LDAP user import.
    """

    grok.name('sync_user')

    def run_update(self):
        self.log("Starting user import...")
        updater = IOGDSUpdater(self.context)
        updater.import_users()


class GroupSyncView(LDAPSyncView):
    """Browser view that starts an LDAP group import.
    """

    grok.name('sync_group')

    def run_update(self):
        self.log("Starting groups import...")
        updater = IOGDSUpdater(self.context)
        updater.import_groups()


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
