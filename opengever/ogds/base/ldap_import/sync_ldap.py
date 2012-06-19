import sys
import ldap
from collective.transmogrifier.transmogrifier import Transmogrifier
import transaction
from Testing.makerequest import makerequest
from AccessControl.SecurityManagement import newSecurityManager
from zope.app.component.hooks import setSite
from optparse import OptionParser
from opengever.ogds.base.ldap_import.import_stamp import \
    set_remote_import_stamp


CONFIGS = u'opengever.ogds.base.user-import;opengever.ogds.base.group-import'


def debugAfterException():
    """Starts pdb at the point where an uncatched exception was raised.
    """

    def info(type, value, tb):
        if hasattr(sys, 'ps1') or not sys.stderr.isatty():
            # we are in interactive mode or we don't have a tty-like
            # device, so we call the default hook
            sys.__excepthook__(type, value, tb)
        else:
            import traceback
            import pdb
            # we are NOT in interactive mode, print the exception...
            traceback.print_exception(type, value, tb)
            print
            # ...then start the debugger in post-mortem mode.
            pdb.pm()

    sys.excepthook = info


def check_if_ldap_reachable(site):
    """This function gets the LDAP server from the
    LDAPUserFolder Plugin on the Plone site and tries
    to establish a connection.

    If for some reason we can't get a connection to the LDAP,
    we abort the entire import, because otherwise we would
    end up with all users being set to inactive since they
    can't be found in the LDAP.
    """

    ldap_folder = site.acl_users.get('ldap').get('acl_users')
    server = ldap_folder.getServers()[0]
    ldap_url = "%s://%s:%s" % (
        server['protocol'], server['host'], server['port'])
    ldap_conn = ldap.initialize(ldap_url)
    try:
        ldap_conn.search_s(ldap_folder.users_base, ldap.SCOPE_SUBTREE)
    except ldap.LDAPError, e:
        # If for some reason we can't get a connection to the LDAP,
        # we abort the entire import, because otherwise we would
        # end up with all users being set to inactive since they
        # can't be found in the LDAP.
        print "ERROR: Couldn't connect to LDAP server: %s %s" % (
            e.__class__.__name__, e)
        print "The import has been aborted."
        transaction.abort()
        sys.exit(1)


def run_import(app, options):
    # setup request and get plone site
    app = makerequest(app)
    plone = app.unrestrictedTraverse(options.site_root)

    check_if_ldap_reachable(plone)

    # setup user context
    user = app.acl_users.getUser('zopemaster')
    user = user.__of__(app.acl_users)
    newSecurityManager(app, user)

    #setup site
    setSite(plone)

    transmogrifier = Transmogrifier(plone)

    trans_configs = options.config.split(';')
    for config in trans_configs:

        print "Importing..."
        import time
        now = time.clock()
        transmogrifier(config)

        #transmogrifier(u'opengever.repository1.ska-arch')
        #transmogrifier(u'opengever.konsulmigration.repository')
        elapsed = time.clock() - now
        print "Done in %.0f seconds." % elapsed
        print "Committing transaction..."
        transaction.commit()

    if len(trans_configs) != 0 and options.update_syncstamp:
        print "update LDAP SYNC importstamp"
        set_remote_import_stamp(plone)
        transaction.commit()
    print "Done"


def main():

    # check if we have a zope environment aka 'app'
    mod = __import__(__name__)
    if not ('app' in dir(mod) or 'app' in globals()):
        print "Must be run with 'bin/instance run'."
        return

    parser = OptionParser()
    parser.add_option(
        "-D", "--debug", action="store_true", dest="debug", default=False)
    parser.add_option("-c", "--config", dest="config",
                  default=CONFIGS)
    parser.add_option('-u', "--update-syncstamp",
                      dest="update_syncstamp", default=True)
    parser.add_option("-s", "--site-root",
                      dest="site_root", default=u'/Plone')

    (options, args) = parser.parse_args()

    if options.debug:
        debugAfterException()

    run_import(app, options)

if __name__ == '__main__':
    main()
