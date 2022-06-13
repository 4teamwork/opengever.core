from ftw.testbrowser import LIB_REQUESTS
from xml.etree import ElementTree


WEBDAV_TIMEOUT = 'Infinite, Second-4100000000'
DAV_NAMESPACES = {'D': 'DAV:'}


class TestOfficeConnector(object):
    """Helper to make OfficeConnector webdav requests to GEVER during testing.

    """
    def __init__(self, context, browser):
        self.context = context
        self.browser = browser
        self.lock_token = None

    def _extract_lock_token(self, xml):
        # XXX: Zope returns wrong Namespace for owner content.
        if 'xmlns:d="DAV:"' in xml:
            xml = xml.strip().replace(
                '<D:href>', '<d:href>').replace('</D:href>', '</d:href>')

        try:
            xmldoc = ElementTree.fromstring(xml)
        except ElementTree.ParseError:
            xmldoc = ElementTree.Element('')
        token_el = xmldoc.find(
            "./D:lockdiscovery/D:activelock/D:locktoken/D:href",
            DAV_NAMESPACES)
        if token_el is not None:
            return token_el.text
        else:
            return None

    def _request(self, method, body=None, headers=None):
        url = self.browser._normalize_url(self.context)
        driver = self.browser.get_driver(LIB_REQUESTS)
        driver.make_request(method, url, data=body, headers=headers)
        return driver.response

    def lock(self):
        """Issue a LOCK request for context.

        Also acquires a lock-token for refreshing/unlocking.
        """
        headers = {
            'Content-Type': 'text/xml; charset="utf-8"',
            'Timeout': WEBDAV_TIMEOUT,
            'Depth': '0',
        }

        body = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<D:lockinfo xmlns:D="DAV:">\n'
            '  <D:lockscope><D:exclusive/></D:lockscope>\n'
            '  <D:locktype><D:write/></D:locktype>\n'
            '  <D:owner>\n'
            '  <D:href>Office Connector</D:href>\n'
            '  </D:owner>\n'
            '</D:lockinfo>'
        )

        response = self._request('LOCK', body=body, headers=headers)
        self.lock_token = self._extract_lock_token(response.text)

    def unlock(self):
        """Issue an UNLOCK request for a previously locked context."""

        assert self.lock_token, 'must LOCK first.'
        headers = {
            'Lock-Token': self.lock_token,
            'If': '(<{}>)'.format(self.lock_token),
        }
        self._request('UNLOCK', headers=headers)
