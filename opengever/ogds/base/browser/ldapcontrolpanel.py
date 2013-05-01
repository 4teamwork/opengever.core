from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from collective.transmogrifier.transmogrifier import Transmogrifier
from five import grok
from ftw.dictstorage.interfaces import IDictStorage
from opengever.ogds.base.interfaces import ISyncStamp
from opengever.ogds.base.ldap_import.import_stamp import DICTSTORAGE_SYNC_KEY
from opengever.ogds.base.ldap_import.import_stamp import \
    set_remote_import_stamp
from opengever.ogds.base.ldap_import.import_stamp import \
    DictStorageConfigurationContext
from time import strftime
from zope.component import getUtility
import ldap
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
        storage = IDictStorage(DictStorageConfigurationContext())
        timestamp = storage.get(DICTSTORAGE_SYNC_KEY)
        return timestamp


class UserSyncView(grok.View):
    """A view wich start the ldap group synchronisation """

    grok.name('sync_user')
    grok.context(IPloneSiteRoot)
    grok.require('cmf.ManagePortal')

    configuration = 'opengever.ogds.base.user-import'

    def mklog(self):
        """ helper to prepend a time stamp to the output """
        write = self.request.RESPONSE.write

        def log(msg, timestamp=True):
            if timestamp:
                msg = '%s : %s \n' % (strftime('%Y/%m/%d-%H:%M:%S '), msg)
            write(msg)
        return log

    def render(self):

        log = self.mklog()

        # check if ldap is reachable
        log('Check if LDAP import is reachable')
        ldap_folder = self.context.acl_users.get('ldap').get('acl_users')
        server = ldap_folder.getServers()[0]
        ldap_url = "%s://%s:%s" % (
            server['protocol'], server['host'], server['port'])
        ldap_conn = ldap.initialize(ldap_url)
        try:
            ldap_conn.search_s(ldap_folder.users_base, ldap.SCOPE_SUBTREE)
        except ldap.LDAPError, e:
            return "LDAP is not reachable. \
                Couldn't start Group import. LDAPError: %s" % (e)
        now = time.clock()

        transmogrifier = Transmogrifier(self.context)

        log("Start user import")
        transmogrifier(self.configuration)
        transaction.commit()
        elapsed = time.clock() - now
        log("Done in %.0f seconds." % elapsed)

        if self.configuration:
            print "update LDAP SYNC importstamp"
            set_remote_import_stamp(self.context)
            transaction.commit()

        log("Committing transaction...")

        log('Done user import')


class GroupSyncView(UserSyncView):
    """This View provides the same functinality like the parent,
    just start the group import"""

    grok.name('sync_group')
    grok.context(IPloneSiteRoot)
    grok.require('cmf.ManagePortal')

    configuration = 'opengever.ogds.base.group-import'


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
