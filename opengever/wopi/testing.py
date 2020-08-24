from base64 import b64encode
from opengever.wopi import discovery
from opengever.wopi.interfaces import IWOPISettings
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import time


def int2bytes(val, num_bytes):
    return ''.join([
        chr((val & (0xff << pos * 8)) >> pos * 8)
        for pos in reversed(range(num_bytes))
    ])


def mock_wopi_discovery(extensions=None, public_key=None):
    if not extensions:
        extensions = ['docx', 'xlsx', 'pptx']
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IWOPISettings)
    settings.enabled = True
    settings.discovery_url = u'http://localhost/hosting/discovery'
    discovery._WOPI_DISCOVERY = {
        'timestamp': time.time(),
        'url': settings.discovery_url,
        'editable-extensions': set(extensions),
    }
    if public_key is not None:
        modulus = b64encode(int2bytes(public_key.public_numbers().n, 256))
        discovery._WOPI_DISCOVERY['proof-key'] = {
             '@exponent': 'AQAB',
             '@modulus': modulus,
             '@oldexponent': 'AQAB',
             '@oldmodulus': modulus,
        }
