from plone.restapi.services import Service
from ftw.bumblebee.usersalt import get_user_salt
from ftw.bumblebee.hashing import get_derived_secret
from ftw.bumblebee.utils import get_cookie_name
from base64 import b64encode
import json
import hashlib
import hmac


class BumblebeeSession(Service):
    """Create a bumblebee session"""

    def reply(self):

        payload = {'salt': get_user_salt()}
        secret = get_derived_secret('salt cookie')
        encoded_payload = b64encode(
            json.dumps(payload, sort_keys=True)).strip()
        hash_ = hmac.new(secret, encoded_payload, hashlib.sha1).hexdigest()
        cookie_value = '--'.join((encoded_payload, hash_))

        self.request.response.setCookie(
            get_cookie_name(), cookie_value, path='/')

        return super(BumblebeeSession, self).reply()
