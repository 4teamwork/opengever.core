from config import SESSION_COOKIES_FILE
from os.path import isfile
import json


API_POST_HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
}

# Cookie params that the CookieJar doesn't allow us to set
UNSUPPORTED_COOKIE_PARAMS = [
    '_rest',
    'path_specified',
    'domain_specified',
    'port_specified',
    'domain_initial_dot',
]


def login_to_portal(browser, cluster, username, password):
    """Performs a login to the portal, using given username and password.

    Returns the username of the logged in user, and the cookies received in
    the response. These cookies contain the portal session, and can be
    stored and loaded to avoid logging in all the time.
    """
    if cluster.new_portal:
        payload = json.dumps({
            'username': username,
            'password': password,
            'remember_me': False,
            'invitation': ""})

        login_api_url = '/'.join((cluster.portal_url, 'api', 'login'))
        browser.open(login_api_url,
                     method='POST',
                     headers=API_POST_HEADERS, data=payload)

        expected_response = {
            'username': username,
            'state': 'logged_in',
            'invitation_callback': ''}

        if not expected_response == browser.json:
            print "Login failed: %r" % browser.contents

    else:
        login_url = '/'.join((cluster.portal_url, 'login'))

        browser.open(login_url)
        browser.fill({'Benutzername': username, 'Passwort': password}).submit()
        # TODO: Check for login success, and maybe raise a LoginFailed
        # exception here so we can distinguish this case.

    # Extract and clean up cookies from response
    cookies = dict(browser.cookies)
    for cookie_name, cookie_data in cookies.items():
        for param_to_remove in UNSUPPORTED_COOKIE_PARAMS:
            cookies[cookie_name].pop(param_to_remove, None)

    return username, cookies


def load_session_cookies():
    """Load stored session cookies from file.
    """
    if not isfile(SESSION_COOKIES_FILE):
        return {}

    with open(SESSION_COOKIES_FILE, 'r') as cookies_file:
        return json.load(cookies_file)


def store_session_cookies(session_cookies):
    """Store session cookies to file, overwriting existing ones.
    """
    with open(SESSION_COOKIES_FILE, 'w') as cookies_file:
        json.dump(session_cookies, cookies_file,
                  sort_keys=True, indent=4, separators=(',', ': '))


def login_and_store(browser, cluster, username, password):
    """Log in, and store session cookies to file (keyed by cluster URL).

    If cookies already exist for the given cluster, they get updated.
    Cookies for other clusters are left untouched.
    """
    logged_in_user, cookies = login_to_portal(
        browser, cluster, username, password)

    session_cookies = load_session_cookies()
    cookie_set = {cluster.url: {'username': username,
                                'cookies': cookies}}
    session_cookies.update(cookie_set)
    store_session_cookies(session_cookies)
