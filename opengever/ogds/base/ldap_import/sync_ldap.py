from collective.transmogrifier.transmogrifier import Transmogrifier
import transaction
from Testing.makerequest import makerequest
from AccessControl.SecurityManagement import newSecurityManager
from zope.app.component.hooks import setSite
from optparse import OptionParser


def debugAfterException():
    """Starts pdb at the point where an uncatched exception was raised.
    """

    import sys

    def info(type, value, tb):
       if hasattr(sys, 'ps1') or not sys.stderr.isatty():
          # we are in interactive mode or we don't have a tty-like
          # device, so we call the default hook
          sys.__excepthook__(type, value, tb)
       else:
          import traceback, pdb
          # we are NOT in interactive mode, print the exception...
          traceback.print_exception(type, value, tb)
          print
          # ...then start the debugger in post-mortem mode.
          pdb.pm()

    sys.excepthook = info

def run_import(app, options):

    # setup request and get plone site
    app=makerequest(app)
    plone = app.unrestrictedTraverse(options.site_root)

    # setup user context
    user = app.acl_users.getUser('zopemaster')
    user = user.__of__(app.acl_users)
    newSecurityManager(app, user)

    #setup site
    setSite(plone)

    transmogrifier = Transmogrifier(plone)

    print "Importing..."
    import time
    now = time.clock()
    transmogrifier(options.config)
    #transmogrifier(u'opengever.repository1.ska-arch')
    #transmogrifier(u'opengever.konsulmigration.repository')
    elapsed = time.clock()-now
    print "Done in %.0f seconds." % elapsed
    print "Committing transaction..."
    transaction.commit()
    print "Done"


def main():

    # check if we have a zope environment aka 'app'
    mod = __import__(__name__)
    if 'app' not in dir(mod):
        print "Must be run with 'zopectl run'."
        return

    parser = OptionParser()
    parser.add_option("-D", "--debug", action="store_true", dest="debug", default=False)
    parser.add_option("-c", "--config", dest="config", default=u'opengever.ogds.base.user-import')
    parser.add_option("-s", "--site-root", dest="site_root", default=u'/Plone')
    (options, args) = parser.parse_args()

    if options.debug:
        debugAfterException()
    
    run_import(app, options)

if __name__ == '__main__':
    main()
