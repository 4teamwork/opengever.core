from plone.keyring.interfaces import IKeyManager
from struct import pack
from time import time
from zope.component import getUtility
import hashlib
import hmac


def create_access_token(userid, scope, timestamp=None, secret=None):
    if secret is None:
        manager = getUtility(IKeyManager)
        secret = manager.secret()

    if timestamp is None:
        timestamp = int(time())

    digest = hmac.new(
        secret, userid + scope + pack("!I", timestamp),
        hashlib.sha256).digest()
    token = "%s%08x%s" % (digest, timestamp, userid)
    return token


def validate_access_token(token, scope, ttl=43200):
    if not isinstance(token, str) or len(token) < 42:
        return None
    digest = token[:32]

    timestamp = token[32:40]
    timestamp = int(timestamp, 16)
    if time() - timestamp > ttl:
        return None

    userid = token[40:]

    new_token = create_access_token(userid, scope, timestamp=timestamp)
    if is_equal(digest, new_token[:32]):
        return userid
    return None


def is_equal(val1, val2):
    """Time-constant string comparison"""
    if not isinstance(val1, basestring) or not isinstance(val2, basestring):
        return False
    if len(val1) != len(val2):
        return False
    result = 0
    for x, y in zip(val1, val2):
        result |= ord(x) ^ ord(y)
    return result == 0
