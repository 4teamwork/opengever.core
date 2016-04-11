from urlparse import urljoin
from urlparse import urlparse
import requests


class RelativeSession(requests.Session):
    """A session that takes a base URL and makes requests relative to that
    base if their URL is relative (doesn't begin with a HTTP[S] scheme).
    """

    def __init__(self, base_url):
        super(RelativeSession, self).__init__()
        if not base_url.endswith('/'):
            base_url += '/'
        self.__base_url = base_url

    def request(self, method, url, **kwargs):
        if urlparse(url).scheme not in ('http', 'https'):
            url = url.lstrip('/')
            url = urljoin(self.__base_url, url)
        return super(RelativeSession, self).request(method, url, **kwargs)
