from auth import load_session_cookies
from auth import login_and_store
from colors import green
from colors import red
from colors import white
from colors import yellow
from config import AdminUnit
from config import SESSION_COOKIES_DIR
from config import SESSION_COOKIES_FILE
from ftw.testbrowser import browser
from ftw.testbrowser.core import LIB_REQUESTS
from getpass import getpass
from os.path import expanduser
from requests.cookies import create_cookie
import errno
import os
import sys
import traceback


class MissingStoredSessionCookies(Exception):
    """Unable to find stored session cookies for given cluster.
    """


class CookieLoaderMixin(object):
    """Handles loading of stored session cookies.
    """

    def get_session_cookies(self, cluster):
        """Load session cookies for a specific cluster.
        """
        session_cookies = load_session_cookies()

        cookies = session_cookies.get(cluster.url, {}).get('cookies')
        if not cookies:
            raise MissingStoredSessionCookies

        return cookies

    def add_cookies(self, browser, cookies):
        """Given a browser and a set of cookies, add them to the browser.
        """
        driver = browser.get_driver()
        for cookie_data in cookies.values():
            cookie = create_cookie(**cookie_data)
            driver.requests_session.cookies.set_cookie(cookie)

    def create_session_cookies_dir(self):
        self.mkdir_p(expanduser(SESSION_COOKIES_DIR))

    def mkdir_p(self, path):
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >=2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise


class SmokeTestRunner(CookieLoaderMixin):

    def __init__(self, clusters, tests_by_type,
                 prompt_credentials=False):
        self.clusters = clusters
        self.tests_by_type = tests_by_type
        self.create_session_cookies_dir()

        self.skipped_tests = False

        # Configure requests driver for all testbrowser requests
        browser.default_driver = LIB_REQUESTS

        if prompt_credentials:
            self.prompt_for_credentials()

    def prompt_for_credentials(self):
        print "Please enter credentials for the following clusters."
        print "These will be used to login to the corresponding portal, "
        print "and save the Portal session cookies to %s" % SESSION_COOKIES_FILE
        print "The password itself will never be saved."
        print

        for cluster in self.clusters:
            with browser:
                print "Cluster: %s" % cluster.url
                username = raw_input('Username: ')
                password = getpass('Password: ')
                login_and_store(browser, cluster, username, password)
                print "-" * 80
                print

    def run_tests(self):
        for cluster in self.clusters:
            self.test_cluster(cluster)
        if self.skipped_tests:
            print
            print "Some tests have been skipped because no stored credentials"
            print "could be found for them. Re-run this script with "
            print "--prompt-credentials to be prompted for credentials."
            print "They will then be stored for subsequent runs."

    def test_cluster(self, cluster):
        print "\nTesting Cluster: %s" % cluster.url
        print "=" * 80

        for cluster_level_test in self.tests_by_type['cluster']:
            self.run_single_test(cluster_level_test, args=(cluster, ))

        for admin_unit in cluster.admin_units:
            for au_level_test in self.tests_by_type['admin_unit']:
                self.run_single_test(au_level_test, args=(admin_unit, ))

    def run_single_test(self, test, args):
        test_details = '%-50s %r' % (white(test.__name__), args)

        # Determine cluster. `args` are test arguments, which currently are a
        # one-tuple of either an AdminUnit or a Cluster entity.
        entity = args[0]
        if isinstance(entity, AdminUnit):
            cluster = entity.cluster
        else:
            cluster = entity

        try:
            with browser:
                if test in self.tests_by_type['logged_in']:
                    # Test expects a browser that is set up with a valid
                    # portal session. Add session cookies if available.
                    try:
                        cookies = self.get_session_cookies(cluster)
                    except MissingStoredSessionCookies:
                        test_details += ' (Missing stored session cookies)'
                        print '%s - %s' % (yellow('SKIP'), test_details)
                        self.skipped_tests = True
                        return
                    self.add_cookies(browser, cookies)

                # Run the actual test
                test(browser, *args)
            print '%s - %s' % (green('PASS'), test_details)

        except Exception:
            print '%s - %s' % (red('\nFAIL'), test_details)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb = ''.join(traceback.format_exception(
                exc_type, exc_value, exc_traceback))
            print tb
