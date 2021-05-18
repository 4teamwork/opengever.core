from collective.clamav.interfaces import IAVScanner
from six import BytesIO
from zope.interface import implements
import clamd


class ScanError(Exception):
    """Generic exception for AV checks.
    """

    def __init__(self, message):
        super(ScanError, self).__init__(message)


def _make_clamd(type, **kwargs):
    timeout = kwargs.get('timeout', 10.0)
    if type == 'socket':
        socketpath = kwargs.get('socketpath', '/var/run/clamd')
        return clamd.ClamdUnixSocket(path=socketpath, timeout=timeout)
    elif type == 'net':
        host = kwargs.get('host', 'localhost')
        port = kwargs.get('port', 3310)
        return clamd.ClamdNetworkSocket(host=host, port=port, timeout=timeout)
    else:
        raise ScanError('Invalid call')


class ClamavScanner(object):
    """
    """
    implements(IAVScanner)

    def ping(self, type, **kwargs):
        if not _make_clamd(type, **kwargs).ping() == "PONG":
            raise ScanError('Could not ping clamd server')
        return True

    def scanBuffer(self, buffer, type, **kwargs):
        """Scans a buffer for viruses
        """
        return self.scanStream(BytesIO(buffer), type, **kwargs)

    def scanStream(self, stream, type, **kwargs):
        """Scans a stream for viruses
        """

        timeout = kwargs.get('timeout', 120.0)
        kwargs_copy = dict(kwargs)
        kwargs_copy.update(timeout=timeout)
        cd = _make_clamd(type, **kwargs_copy)
        status = cd.instream(stream)

        if status["stream"][0] == "FOUND":
            return status["stream"][1]
        if status["stream"][0] == "ERROR":
            raise ScanError(status["stream"][1])
