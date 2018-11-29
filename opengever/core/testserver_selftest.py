from ftw.testbrowser import browser
from ftw.testbrowser.pages import factoriesmenu
from plone.app.testing.interfaces import SITE_OWNER_NAME
from plone.app.testing.interfaces import SITE_OWNER_PASSWORD
from threading import Thread
from time import sleep
import os
import signal
import socket
import subprocess
import sys
import xmlrpclib


class TestserverSelftest(object):
    """The selftest tests that the testserver works properly.
    The selftest is not a regular unittest so that it does not run together
    with the regular tests. It is too time consuming.
    """

    def __call__(self):
        os.environ['ZSERVER_PORT'] = os.environ.get('ZSERVER_PORT', '60601')
        self.plone_url = 'http://localhost:{}/plone/'.format(os.environ['ZSERVER_PORT'])
        os.environ['TESTSERVER_CTL_PORT'] = os.environ.get('PORT1', '60602')

        self.controller_proxy = xmlrpclib.ServerProxy('http://localhost:{}'.format(
            os.environ['TESTSERVER_CTL_PORT']))
        print ansi_green('> STARTING TESTSERVER')
        self.start_testserver()
        try:
            self.wait_for_testserver()
            print ansi_green('> TESTSERVER IS READY')
            print ansi_green('> PERFORMING SELFTEST')
            self.selftest()
        finally:
            print ansi_green('> STOPPING TESTSERVER')
            self.stop_testserver()

    def selftest(self):
        with browser:
            self.testserverctl('zodb_setup')
            with browser.expect_unauthorized():
                browser.open(self.plone_url)
            browser.fill({'Benutzername': SITE_OWNER_NAME,
                          'Passwort': SITE_OWNER_PASSWORD}).submit()
            factoriesmenu.add('Ordnungssystem')
            browser.fill({'Titel': 'Testerver Selftest'}).submit()
            browser.open(self.plone_url)
            assert 'Testerver Selftest' in browser.css('#navi li').text
            self.testserverctl('zodb_teardown')

            self.testserverctl('zodb_setup')
            browser.open(self.plone_url)
            assert 'Testerver Selftest' not in browser.css('#navi li').text
            self.testserverctl('zodb_teardown')

    def testserverctl(self, *args):
        args = ['bin/testserverctl'] + list(args)
        print ansi_blue('>', *args)
        subprocess.check_call(args)

    def start_testserver(self):
        """Start the testserver in a subprocess controlled by a separate thread.
        """
        args = ['bin/testserver']
        print ansi_blue('>', *args)
        self.testserver_process = subprocess.Popen(args)
        self.testserver_thread = Thread(target=self.testserver_process.communicate)
        self.testserver_thread.start()

    def wait_for_testserver(self):
        """Block until the testserver is ready.
        """
        timeout_seconds = 60 * 60
        interval = 0.1
        steps = timeout_seconds / interval
        for second in range(int(steps)):
            if self.is_controller_server_ready():
                return
            sleep(interval)

        self.stop_testserver()
        raise Exception('Timeout: testserver did not start in {} seconds'.format(timeout_seconds))

    def stop_testserver(self):
        """Kill the testserver process group.
        It should be killed as group since bin/testserver is a wrapper script,
        creating a subprocess.
        """
        try:
            os.killpg(os.getpgid(self.testserver_process.pid), signal.SIGINT)
        except KeyboardInterrupt:
            # XXX Somehow the main process also receives a SIGINT.
            pass
        self.testserver_thread.join()

    def is_controller_server_ready(self):
        """Test whether the controller server is available.
        This indicates that the testserver is ready.
        """
        try:
            self.controller_proxy.listMethods()
        except socket.error:
            return False
        except Exception:
            pass
        return True


def ansi_green(*text):
    text = ' '.join(text)
    if sys.stdout.isatty():
        return '\033[0;32m{}\033[0m'.format(text)
    else:
        return text


def ansi_blue(*text):
    text = ' '.join(text)
    if sys.stdout.isatty():
        return '\033[0;34m{}\033[0m'.format(text)
    else:
        return text


def selftest():
    TestserverSelftest()()
