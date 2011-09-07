from collective.transmogrifier.transmogrifier import Transmogrifier
from five import grok
from Products.CMFPlone.interfaces import IPloneSiteRoot
import ldap
import time
import transaction
from time import strftime


class LDAPControlPanel(grok.View):
    """Displays infos and links about and for the ldap synchronisation
    """

    grok.name('ldap_controlpanel')
    grok.context(IPloneSiteRoot)
    grok.require('cmf.ManagePortal')


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
            return "LDAP is not reachable. Couldn't start Group import. LDAPError: %s" %(e)
        now = time.clock()

        transmogrifier = Transmogrifier(self.context)

        log("Start user import")
        transmogrifier(self.configuration)

        elapsed = time.clock() - now
        log("Done in %.0f seconds." % elapsed)
        log("Committing transaction...")
        transaction.commit()

        log('Done user import')


class GroupSyncView(UserSyncView):
    """This View provides the same functinality like the parent,
    just start the group import"""

    grok.name('sync_group')
    grok.context(IPloneSiteRoot)
    grok.require('cmf.ManagePortal')

    configuration = 'opengever.ogds.base.group-import'
