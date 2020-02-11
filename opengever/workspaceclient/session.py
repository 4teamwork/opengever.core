from opengever.workspaceclient.exceptions import APIRequestException
from opengever.workspaceclient.keys import key_registry
from requests import HTTPError
import jwt
import pkg_resources
import requests
import threading
import time
import os


SESSION_STORAGE = threading.local()
GRANT_TYPE = "urn:ietf:params:oauth:grant-type:jwt-bearer"
GEVER_VERSION = pkg_resources.get_distribution('opengever.core').version


class FtwTokenAuthSession(requests.Session):
    """This Session class takes care of the authentication token. It will
    auto-renew the access-token as soon as it is expired.

    In addition, it binds the request to the base_url. Requests made by
    this session object will always prepend the base_url to the request-url.
    This allows us to use relative urls for further requests.

    Example usage of this session object:

    session = FtwTokenAuthSession('http://example.com', service_key, 'test.user')
    session.get('folder-1')  # will resolve to 'http://example.com/folder-1'
    """
    session_expiration_seconds = 60 * 60

    def __init__(self, base_url, service_key, username):
        super(FtwTokenAuthSession, self).__init__()
        self.base_url = base_url.strip('/')
        self.service_key = service_key
        self.username = username

    def request(self, method, path_or_url, *args, **kwargs):
        url = self.url_from_path_or_url(path_or_url)
        response = super(FtwTokenAuthSession, self).request(method, url,
                                                            *args, **kwargs)

        if self.token_has_expired(response):
            # We got an 'Access token expired' response => refresh token
            self.obtain_token()
            # Re-dispatch the request that previously failed
            response = super(FtwTokenAuthSession, self).request(method, url,
                                                                *args, **kwargs)

        self.raise_for_status(response)

        return response

    def token_has_expired(self, response):
        status = response.status_code
        content_type = response.headers['Content-Type']

        if status == 401 and content_type == 'application/json':
            body = response.json()
            if body.get('error_description') == 'Access token expired':
                return True

        return False

    def obtain_token(self):
        """Acquires a fresh authorization token from the workspace and sets it
        in the current session.
        """
        claim_set = {
            "iss": self.service_key["client_id"],
            "sub": self.username,
            "aud": self.service_key["token_uri"],
            "iat": int(unfrozen_time()),
            "exp": int(unfrozen_time() + self.session_expiration_seconds),
        }

        grant = jwt.encode(claim_set, self.service_key["private_key"], algorithm="RS256")
        payload = {"grant_type": GRANT_TYPE, "assertion": grant}

        response = requests.post(self.service_key["token_uri"], data=payload,
                                 headers={"Accept": "application/json"})

        self.raise_for_status(response)

        bearer_token = response.json()["access_token"]
        self.headers.update({"Authorization": "Bearer {}".format(bearer_token)})

    def raise_for_status(self, response):
        try:
            response.raise_for_status()
        except HTTPError as exception:
            raise APIRequestException(exception)

    def url_from_path_or_url(self, path_or_url):
        """Generates a url based on the path_or_url:

        1. Path "workspace-1/folder-1"

        1a. replace base_url: workspace-1/folder-1 => workspace-1/folder-1
        1b. prepend base_url: workspace-1/folder-1 => http://example.com/workspace-1/folder-1

        2. URL "http://example.com/workspace-1/folder-1"

        2a. replace base_url: http://example.com/workspace-1/folder-1 => workspace-1/folder-1
        1b. prepend base_url: workspace-1/folder-1 => http://example.com/workspace-1/folder-1
        """
        path = path_or_url.replace(self.base_url, '')
        return '/'.join([self.base_url, path.lstrip('/')]).strip('/')


class WorkspaceSession(object):
    """The WorkspaceSession object provides a preconfigured request session for
    a workspace.
    The requests session is reused for multiple requests so that we have a smaller
    footprint regarding oauth authentication requests. The session is cached in memory.
    The WorkspaceSession is instantiated with a workspace url (to any ressource)
    and the operating user.
    """

    def __init__(self, workspace_url, username):
        self.workspace_url = workspace_url
        self.username = username
        self.session = self._get_or_create_session()

    @property
    def request(self):
        """Returns the current session to perform a request.
        """
        return self.session

    @staticmethod
    def clear():
        """Clear all caches.
        """
        SESSION_STORAGE.sessions = None

    def _get_or_create_session(self):
        """Returns a ``requests`` session for the GEVER client with the given url.
        The session may be outdated. The session is reused over multiple
        requests by the same person.
        """
        if getattr(SESSION_STORAGE, "sessions", None) is None:
            SESSION_STORAGE.sessions = {}

        if self._unique_session_key not in SESSION_STORAGE.sessions:
            SESSION_STORAGE.sessions[self._unique_session_key] = self._make_session()

        return SESSION_STORAGE.sessions[self._unique_session_key]

    def _make_session(self):
        """Create a fresh requests session and return it.
        """
        service_key = key_registry.get_key_for(self.workspace_url)
        session = FtwTokenAuthSession(self.workspace_url, service_key, self.username)
        session.headers.update({"User-Agent": self._user_agent})
        session.headers.update({"Accept": "application/json"})
        session.obtain_token()
        return session

    @property
    def _unique_session_key(self):
        return (self.workspace_url, self.username)

    @property
    def _user_agent(self):
        custom_user_agent = os.environ.get('OPENGEVER_APICLIENT_USER_AGENT', '')
        return 'opengever.core/{} {}'.format(
            GEVER_VERSION, custom_user_agent).strip()


def unfrozen_time(*args, **kwargs):
    """In testing, we want to be able to freeze the time. But we never want to freeze
    the time when generating JWT access tokens for accessing other systems.
    The unfrozen_time function makes sure to always return a real time, no matter
    whether the time is frozen or the freezegun is even installed.
    """
    try:
        from freezegun.api import real_time
    except ImportError:
        return time.time(*args, **kwargs)
    else:
        return real_time(*args, **kwargs)
