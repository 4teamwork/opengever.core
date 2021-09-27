from functools import wraps
from plone.app.robotframework import server as robotframework_server
from six.moves.xmlrpc_server import SimpleXMLRPCServer
from ZPublisher import Publish
import argparse
import logging
import os
import sys
import time


"""To make e2e tests more robust during teardown/setup of the zodb, we have
to provide a way to do it in one single request. Unfortunately, the
robotframwork does not provide such a method.

Thus, we decided to override the Zope2Server from the robotframework to
provide an 'isolate' method which tears-down the zodb if necessary and directly
sets it up.

We make this method available through the xmlrpc server.
This allows us to teardown/setup the database in one single request.
"""


class IsolationReadinessTimeout(Exception):

    def __init__(self, timeout):
        super(IsolationReadinessTimeout, self).__init__(
            'Timeout awaiting isolation readiness (after {} seconds).'.format(timeout))


class IsolationReadiness(object):
    """This singleton object knows whether test setup / isolation is
    finished and the testserver is ready to handle requests.
    This is important, so that the testserver is sturdy enough for
    randomly timed requests from the client.
    """

    def __init__(self):
        self._ready = False

    def teardown_started(self):
        self._ready = False

    def setup_finished(self):
        self._ready = True

    def await_ready(self, timeout_s=5):
        interval_s = 0.1
        for _ in range(int(timeout_s / interval_s)):
            if self._ready:
                return
            time.sleep(interval_s)
        raise IsolationReadinessTimeout(timeout_s)

    def patch_publisher(self):
        """We are patching the publisher in order to let HTTP requests wait
        until the isolation / test setup has finished.
        If requests are processed while tearing down / setting up, it may
        corrupt the database connection, leaving the testserver in an
        unrecoverable state.
        """
        original = Publish.publish_module_standard

        @wraps(Publish.publish_module_standard)
        def publish_module_standard(module_name,
                                    stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr,
                                    environ=os.environ, debug=0, request=None, response=None):
            try:
                self.await_ready()
            except Exception, exc:
                # XXX this will not properly close the pending HTTP request.
                # I couldn't get that running. I don't think this is very important though,
                # since it would have to be fixed anyway and the exception is visible in the log.
                logging.exception(exc)
                raise
            else:
                return original(module_name, stdin, stdout, stderr, environ, debug, request, response)

        Publish.publish_module_standard = publish_module_standard


ISOLATION_READINESS = IsolationReadiness()


class Zope2Server(robotframework_server.Zope2Server):
    is_zodb_setup = False

    def zodb_setup(self, *args, **kwargs):
        robotframework_server.Zope2Server.zodb_setup(self, *args, **kwargs)
        ISOLATION_READINESS.setup_finished()

    def zodb_teardown(self, *args, **kwargs):
        ISOLATION_READINESS.teardown_started()
        robotframework_server.Zope2Server.zodb_teardown(self, *args, **kwargs)

    def isolate(self, *args, **kwargs):
        if self.is_zodb_setup:
            self.zodb_teardown(*args, **kwargs)

        self.zodb_setup(*args, **kwargs)
        self.is_zodb_setup = True


def start(zope_layer_dotted_name):
    """This is a copy of the plone.app.robotframework.server.start method.

    We just register the additional 'isolate' method here.

    Why not monkey-patching? Because the monkey patch is too late. It has no effect.
    """
    print(robotframework_server.WAIT("Starting Zope 2 server"))

    zsl = Zope2Server()
    zsl.start_zope_server(zope_layer_dotted_name)

    print(robotframework_server.READY("Started Zope 2 server"))

    listener = SimpleXMLRPCServer((robotframework_server.LISTENER_HOST,
                                   robotframework_server.LISTENER_PORT),
                                  logRequests=False)
    listener.allow_none = True
    listener.register_function(zsl.zodb_setup, 'zodb_setup')
    listener.register_function(zsl.zodb_teardown, 'zodb_teardown')
    listener.register_function(zsl.isolate, 'isolate')  # PATCH

    robotframework_server.print_urls(zsl.zope_layer, listener)

    try:
        listener.serve_forever()
    finally:
        print()
        print(robotframework_server.WAIT("Stopping Zope 2 server"))

        zsl.stop_zope_server()

        print(robotframework_server.READY("Zope 2 server stopped"))


def server():
    """This is a copy of the plone.app.robotframework.server.server method.

    This method will be called in the 'bin/testserver' script and is the entry
    point of the Z2 testserver.

    This method directly calls the 'start' method, which we have customized.
    We have to override this method to tell it, that it should use our customized
    'start' method.

    This also means, that we have to provide this method as a console-script in
    'opengever.core.setup'

    Same here, a monkey-patch is too late and does not work.
    """
    if robotframework_server.HAS_RELOAD:
        parser = argparse.ArgumentParser()
    else:
        parser = argparse.ArgumentParser(
            epilog='Note: require \'plone.app.robotframework\' with '
                   '\'[reload]\'-extras to get the automatic code reloading '
                   'support (powered by \'watchdog\').')
    parser.add_argument('layer')
    parser.add_argument('--debug-mode', '-d', dest='debug_mode',
                        action='store_true')
    VERBOSE_HELP = (
        '-v information about test layers setup and tear down, '
        '-vv add logging.WARNING messages, '
        '-vvv add INFO messages, -vvvv add DEBUG messages.')
    parser.add_argument('--verbose', '-v', action='count', help=VERBOSE_HELP)

    if robotframework_server.HAS_RELOAD:
        parser.add_argument('--reload-path', '-p', dest='reload_paths',
                            action='append')
        parser.add_argument('--reload-extensions', '-x', dest='extensions',
                            nargs='*', help=(
                                'file extensions to watch for changes'))
        parser.add_argument('--preload-layer', '-l', dest='preload_layer')
        parser.add_argument('--no-reload', '-n', dest='reload',
                            action='store_false')
    args = parser.parse_args()

    # Set debug mode
    if args.debug_mode is True:
        global HAS_DEBUG_MODE
        HAS_DEBUG_MODE = True

    # Set console log level
    if args.verbose:
        global HAS_VERBOSE_CONSOLE
        HAS_VERBOSE_CONSOLE = True
        loglevel = logging.ERROR - (args.verbose - 1) * 10
        logging.getLogger().addHandler(logging.StreamHandler(sys.stderr))
    else:
        loglevel = logging.ERROR
    logging.basicConfig(level=loglevel)

    # Set reload when available
    if not robotframework_server.HAS_RELOAD or args.reload is False:
        try:
            start(args.layer)
        except KeyboardInterrupt:
            pass
    else:
        robotframework_server.start_reload(
            args.layer, args.reload_paths or ['src'],
            args.preload_layer or 'plone.app.testing.PLONE_FIXTURE',
            args.extensions)
