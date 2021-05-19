from opengever.virusscan.interfaces import IAVScanner
from six import BytesIO
from zope.component import getSiteManager
from zope.interface import implements


EICAR = """
    WDVPIVAlQEFQWzRcUFpYNTQoUF4pN0NDKTd9JEVJQ0FSLVNUQU5E
    QVJELUFOVElWSVJVUy1URVNU\nLUZJTEUhJEgrSCo=\n""".decode('base64')


class MockAVScanner(object):
    """Mock objects to run tests without clamav present.
    """

    implements(IAVScanner)

    uses = 0

    def ping(self, type, **kwargs):
        """
        """
        return True

    def scanStream(self, stream, type, **kwargs):
        """
        """
        self.uses += 1
        if EICAR in stream.read():
            return 'Eicar-Test-Signature FOUND'
        return None

    def scanBuffer(self, buffer, type, **kwargs):
        """
        """
        return self.scanStream(BytesIO(buffer), type, **kwargs)


def register_mock_av_scanner():
    sm = getSiteManager()
    sm.registerUtility(MockAVScanner())
