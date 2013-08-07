from AccessControl.SecurityManagement import newSecurityManager
from App.config import getConfiguration
from opengever.ogds.base.ldap_import.import_stamp import set_remote_import_stamp
from opengever.ogds.base.interfaces import IOGDSUpdater
from optparse import OptionParser
from Testing.makerequest import makerequest
from zope.app.component.hooks import setSite
import ldap
import logging
import sys
import time
import transaction


logger = logging.getLogger('opengever.ogds.base')
LOG_FORMAT = '%(asctime)s %(levelname)s [%(name)s] %(message)s'


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
        logger.error(
            "ERROR: Couldn't connect to LDAP server: %s %s" % (
                e.__class__.__name__, e))
        logger.error("The import has been aborted.")
        transaction.abort()
        sys.exit(1)


def run_import(app, options):
    # setup request and get plone site
    app = makerequest(app)
    plone = app.unrestrictedTraverse(options.site_root)

    # Setup logging
    config = getConfiguration()
    ogds_conf = config.product_config.get('opengever.core', dict())
    log_file = ogds_conf.get('ogds_log_file')

    if log_file:
        log_handler = logging.FileHandler(log_file)
        log_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        log_handler.setFormatter(log_formatter)
        logger.addHandler(log_handler)
        logger.setLevel(logging.INFO)

    check_if_ldap_reachable(plone)

    # setup user context
    user = app.acl_users.getUser('zopemaster')
    user = user.__of__(app.acl_users)
    newSecurityManager(app, user)

    # setup site
    setSite(plone)

    updater = IOGDSUpdater(plone)
    start = time.clock()

    # Import users
    logger.info("Importing users...")
    updater.import_users()

    # Import groups
    logger.info("Importing groups...")
    updater.import_groups()

    elapsed = time.clock() - start
    logger.info("Done in %.0f seconds." % elapsed)
    logger.info("Committing transaction...")
    transaction.commit()

    if options.update_syncstamp:
        # Update sync stamp
        logger.info("Updating LDAP SYNC importstamp...")
        set_remote_import_stamp(plone)
        transaction.commit()

    logger.info("Synchronization Done.")


def main():
    # check if we have a zope environment aka 'app'
    mod = __import__(__name__)
    if not ('app' in dir(mod) or 'app' in globals()):
        print "Must be run with 'bin/instance run'."
        return

    parser = OptionParser()
    parser.add_option("-s", "--site-root",
                      dest="site_root", default=u'/Plone')
    parser.add_option('-u', "--update-syncstamp",
                      dest="update_syncstamp", default=True)
    (options, args) = parser.parse_args()

    run_import(app, options)

if __name__ == '__main__':
    main()
