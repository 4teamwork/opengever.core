from opengever.ogds.base.utils import get_current_admin_unit
from plone.dexterity.utils import safe_utf8
from plone.keyring.interfaces import IKeyManager
from zope.component import getUtility
import jwt
import os


class TokenManager(object):

    def issue_token(self, transfer):
        claims = {
            'jti': os.urandom(16).encode('hex'),
            'iss': get_current_admin_unit().unit_id,
            'iat': transfer.created,
            'exp': transfer.expires,
            'transfer_id': transfer.id,
            'attributes_hash': transfer.attributes_hash(),
        }
        token = jwt.encode(claims, self._signing_secret(), algorithm='HS256')
        transfer.token = token
        return token

    def validate_token(self, transfer, token):
        claims = self._decode_token(token)
        if claims:
            if all([
                token == transfer.token,
                claims['iss'] == get_current_admin_unit().unit_id,
                claims['transfer_id'] == transfer.id,
                claims['attributes_hash'] == transfer.attributes_hash(),
            ]):
                return

        raise InvalidToken()

    def _decode_token(self, token):
        manager = getUtility(IKeyManager)
        for secret in manager[u'_system']:
            if secret is None:
                continue
            claims = self._jwt_decode(token, secret)
            if claims is not None:
                return claims

    def _jwt_decode(self, token, secret):
        token = safe_utf8(token)
        try:
            return jwt.decode(token, secret, verify=True, algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return None

    def _signing_secret(self):
        manager = getUtility(IKeyManager)
        return manager.secret()


class InvalidToken(Exception):
    """Token validation failed.
    """
