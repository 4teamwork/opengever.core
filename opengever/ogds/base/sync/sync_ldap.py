from AccessControl.SecurityManagement import newSecurityManager
from App.config import getConfiguration
from opengever.ogds.base.interfaces import IOGDSUpdater
from opengever.ogds.base.sync.import_stamp import set_remote_import_stamp
from optparse import OptionParser
from Testing.makerequest import makerequest
from zope.app.component.hooks import setSite
import AccessControl
import logging
import time
import transaction


logger = logging.getLogger('opengever.ogds.base')
LOG_FORMAT = '%(asctime)s %(levelname)s [%(name)s] %(message)s'


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

    # setup user context
    user = AccessControl.SecurityManagement.SpecialUsers.system
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
