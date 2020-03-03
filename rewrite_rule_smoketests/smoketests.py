from os.path import abspath
from os.path import dirname
from requests.cookies import create_cookie
from urllib import quote
from urlparse import urlparse
from urlparse import urlunparse


# Hack to allow script to use relative imports when run with bin/zopepy
import sys
sys.path.append(abspath(dirname(__file__)))

from assertions import assert_equal  # noqa
from assertions import assert_in  # noqa
from auth import login_and_store  # noqa
from auth import login_to_portal  # noqa
from colors import green  # noqa
from colors import red  # noqa
from config import AdminUnit  # noqa
from config import Cluster  # noqa
from config import CLUSTERS_TO_TEST  # noqa
from registry import logged_in  # noqa
from registry import on_admin_unit  # noqa
from registry import on_cluster  # noqa
from registry import tests_by_type  # noqa
from runner import SmokeTestRunner  # noqa


@on_cluster
@on_admin_unit
def test_canonical_https_redirect(browser, entity):
    """Tests for presence of canonical HTTPS redirect.

    All URLs that start with a http:// scheme should be redirected to their
    https equivalent.
    """
    expect_trailing_slash = False

    if isinstance(entity, Cluster):
        expect_trailing_slash = True

    # In single unit setups canonical HTTPS redirect adds a trailing
    # slash to the admin unit URL, otherwise it doesn't
    if isinstance(entity, AdminUnit):
        if entity.cluster.single_unit_setup:
            expect_trailing_slash = True

    parsed = urlparse(entity.url)
    http_url = urlunparse(('http', ) + tuple(parsed)[1:])
    https_url = urlunparse(('https', ) + tuple(parsed)[1:])

    browser.allow_redirects = False
    browser.open(http_url)

    expected = https_url
    if expect_trailing_slash:
        expected += '/'

    assert_equal(301, browser.status_code)
    assert_equal(expected, browser.headers['Location'])


@on_admin_unit
def test_teamraum_redirect(browser, admin_unit):
    if not admin_unit.is_dedicated_teamraum:
        return

    browser.allow_redirects = False
    browser.open(admin_unit.url)
    assert_equal(302, browser.status_code)
    assert_equal(admin_unit.front_page_url, browser.headers['Location'])
    assert_equal(True, browser.headers['Location'].endswith('/workspaces'))


@on_admin_unit
def test_anonymous_cas_redirect(browser, admin_unit):
    """Tests that requests to GEVER without authentication cause a redirect

    to the CAS portal.
    """
    browser.allow_redirects = False
    browser.open(admin_unit.front_page_url)

    cluster = admin_unit.cluster

    if cluster.gever_ui_is_default:
        # When the new UI is the default, we won't see a CAS redirect
        # performed by Plone for Anonymous requests. Instead, the frontend
        # app's index.html is served, and the frontend will trigger the CAS
        # redirect.
        assert_equal(200, browser.status_code)
        assert_in('/geverui/assets/', browser.contents)
    else:
        assert_equal(302, browser.status_code)

        service_url = quote(admin_unit.front_page_url + '/')
        cas_login_url = '%s/login?service=%s' % (cluster.portal_url, service_url)
        assert_equal(cas_login_url, browser.headers['Location'])


@on_cluster
def test_portal(browser, cluster):
    browser.open(cluster.portal_url)
    assert_equal(200, browser.status_code)

    if cluster.new_portal:
        # New portal
        assert_equal(cluster.portal_url, browser.url)
        assert_equal(200, browser.status_code)
        assert_in('<script src=/portal/assets/js/app', browser.contents)
    else:
        # Old portal
        username_field = browser.find('Benutzername')
        assert_equal('username', username_field.attrib['name'])

        password_field = browser.find('Passwort')
        assert_equal('password', password_field.attrib['name'])


def test_portal_login(browser, cluster):
    """TODO: Figure out how to conveniently run this test.

    It's currently unregistered because it needs an actual password to test
    the login, and can therefore only run in --prompt-credentials mode.

    It therefore is unregistered for the moment, and doesn't run.
    """
    username = 'foo'
    password = 'bar'

    logged_in_user, cookies = login_to_portal(browser, cluster, username, password)

    if cluster.new_portal:
        assert_equal(200, browser.status_code)
        assert_equal({
            'username': username,
            'state': 'logged_in',
            'invitation_callback': ''},
            browser.json
        )
        assert_in('sessionid', browser.cookies)

    else:
        assert_equal(200, browser.status_code)
        assert_equal(cluster.portal_landingpage_url, browser.url)


@logged_in
@on_cluster
def test_portal_landingpage(browser, cluster):
    browser.allow_redirects = False
    browser.open(cluster.portal_landingpage_url)
    assert_equal(200, browser.status_code)

    if cluster.new_portal:
        # Can't really assert on much more for the new portal.
        assert_in('csrftoken', browser.cookies)
    else:
        logged_in_msg = browser.css('.current-user-info').first.text
        logged_in_msg.startswith('Angemeldet als')


@logged_in
@on_admin_unit
def test_gever_front_page_logged_in_old_ui(browser, admin_unit):
    driver = browser.get_driver()

    cookie_data = {'name': 'geverui', 'value': '0'}
    cookie = create_cookie(**cookie_data)
    driver.requests_session.cookies.set_cookie(cookie)

    browser.open(admin_unit.front_page_url)
    first_heading = browser.css('.documentFirstHeading').first.text

    if admin_unit.is_dedicated_teamraum:
        marker = u'Teamr\xe4ume'
    else:
        marker = u'Pers\xf6nliche \xdcbersicht'

    assert_equal(True, first_heading.startswith(marker))

    logo = browser.css('a#portal-logo').first
    assert_equal(admin_unit.url, logo.attrib['href'])


@on_admin_unit
def test_anonymous_post_requests_always_hit_gever(browser, admin_unit):
    """This is a regression test for a case, where simple POST requests got
    answered with the new frontend's index.html.
    """
    target_url = '/'.join((admin_unit.front_page_url, 'doesnt-exist'))

    browser.raise_http_errors = False
    browser.open(target_url, method='POST')

    assert_equal(404, browser.status_code)

    # Assert we hit Plone by checking for the presence of the logo
    assert_equal(1, len(browser.css('#portal-logo')))


def main():
    prompt_credentials = False
    if '--prompt-credentials' in sys.argv:
        prompt_credentials = True

    runner = SmokeTestRunner(CLUSTERS_TO_TEST, tests_by_type,
                             prompt_credentials=prompt_credentials)
    runner.run_tests()


if __name__ == '__main__':
    main()
