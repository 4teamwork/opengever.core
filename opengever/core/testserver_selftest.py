from ftw.testbrowser import browser
from ftw.testbrowser.pages import factoriesmenu
from plone.app.testing.interfaces import SITE_OWNER_NAME
from plone.app.testing.interfaces import SITE_OWNER_PASSWORD
from threading import Thread
from time import sleep
from urlparse import urlparse
import json
import os
import signal
import socket
import subprocess
import sys
import unittest
import xmlrpclib


class TestserverSelftest(object):
    """The selftest tests that the testserver works properly.
    The selftest is not a regular unittest so that it does not run together
    with the regular tests. It is too time consuming.
    """

    def __init__(self):
        # The TestserverSelftest should not be executed by the regular testserver
        # and therefore should not subclass TestserverSelftest.
        # Lets do a hack so that we have assert methods anyway.
        case = unittest.TestCase('__init__')
        self.assertIn = case.assertIn
        self.assertNotIn = case.assertNotIn
        self.assertEqual = case.assertEqual
        self.assertDictContainsSubset = case.assertDictContainsSubset

    def __call__(self):
        os.environ['ZSERVER_PORT'] = '0'
        os.environ['TESTSERVER_CTL_PORT'] = '0'
        os.environ['PYTHONUNBUFFERED'] = 'true'
        os.environ['SOLR_PORT'] = os.environ.get('PORT3', '19903')

        self.plone_url = None
        self.xmlrpc_url = None

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

            browser.replace_request_header('Accept', 'application/json')
            browser.replace_request_header('Content-Type', 'application/json')

            search_url = self.plone_url + '@solrsearch?fq=path_parent:\\/plone\\/ordnungssystem\\/rechnungspruefungskommission'
            browser.open(search_url)
            self.assertEqual(
                {u'/plone/ordnungssystem/rechnungspruefungskommission': u'createrepositorytree000000000004'},
                {item['path']: item['UID'] for item in browser.json})

            data = {'@type': 'opengever.dossier.businesscasedossier',
                    'title': u'Gesch\xe4ftsdossier',
                    'responsible': 'kathi.barfuss'}
            browser.open(self.plone_url + 'ordnungssystem/rechnungspruefungskommission',
                         method='POST',
                         data=json.dumps(data))
            dossier_url = browser.json['@id']

            browser.open(dossier_url)
            self.assertDictContainsSubset(
                {u'title': u'Gesch\xe4ftsdossier',
                 u'modified': u'2018-11-22T14:29:33+00:00',
                 u'UID': u'testserversession000000000000001',
                 u'email': u'99001@example.org'},
                browser.json)

            browser.open(search_url)
            self.assertEqual(
                {u'/plone/ordnungssystem/rechnungspruefungskommission': u'createrepositorytree000000000004',
                 u'/plone/ordnungssystem/rechnungspruefungskommission/dossier-20': u'testserversession000000000000001'},
                {item['path']: item['UID'] for item in browser.json})

            self.testserverctl('zodb_teardown')
            self.testserverctl('zodb_setup')

            with browser.expect_http_error(404):
                browser.open(dossier_url)

            browser.open(search_url)
            self.assertEqual(
                {u'/plone/ordnungssystem/rechnungspruefungskommission': u'createrepositorytree000000000004'},
                {item['path']: item['UID'] for item in browser.json})

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
        self.testserver_process = subprocess.Popen(args, stdout=subprocess.PIPE)

        def run_and_observe_process():
            while True:
                rc = self.testserver_process.poll()
                if rc is not None:
                    return rc

                line = self.testserver_process.stdout.readline()
                sys.stdout.write(line)
                if not self.plone_url and line.startswith('ZSERVER: '):
                    self.plone_url = '{}/plone/'.format(line[len('ZSERVER: '):].strip())
                if not self.xmlrpc_url and line.startswith('XMLRPC: '):
                    self.xmlrpc_url = line[len('XMLRPC: '):].strip()
                    os.environ['TESTSERVER_CTL_PORT'] = str(urlparse(self.xmlrpc_url).port)

        self.testserver_thread = Thread(target=run_and_observe_process)
        self.testserver_thread.start()

    def wait_for_testserver(self):
        """Block until the testserver is ready.
        """
        timeout_seconds = 60 * 5
        interval = 0.1
        steps = timeout_seconds / interval

        # Wait for urls to be appear. The urls are set from the thread watching
        # the bin/testserver subprocess.
        for num in range(int(steps)):
            if self.xmlrpc_url and self.plone_url:
                break
            if num > 300 and num % 300 == 0:
                print ansi_gray('... waiting for testserver to be ready ')
            sleep(interval)

        # A soon as the URLs appear we can setup the XMLRPC proxy.
        self.controller_proxy = xmlrpclib.ServerProxy(self.xmlrpc_url)

        # Now wait until the server is actually ready.
        for num in range(int(steps)):
            if self.is_controller_server_ready():
                return
            if num > 300 and num % 300 == 0:
                print ansi_gray('... waiting for testserver to be ready ')
            sleep(interval)

        self.stop_testserver()
        raise Exception('Timeout: testserver did not start in {} seconds'.format(timeout_seconds))

    def stop_testserver(self):
        """Kill the testserver process group.
        It should be killed as group since bin/testserver is a wrapper script,
        creating a subprocess.
        """
        try:
            os.kill(self.testserver_process.pid, signal.SIGINT)
        except KeyboardInterrupt:
            pass
        except OSError as exc:
            if exc.strerror != 'No such process':
                raise
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


def ansi_gray(*text):
    text = ' '.join(text)
    if sys.stdout.isatty():
        return '\033[0;36m{}\033[0m'.format(text)
    else:
        return text


def selftest():
    TestserverSelftest()()
