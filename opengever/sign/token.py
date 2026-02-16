from opengever.base.security import elevated_privileges
from opengever.wopi.token import create_access_token
from opengever.wopi.token import validate_access_token
from plone.uuid.interfaces import IUUID
from zope.annotation import IAnnotations


class TokenManager(object):
    """Responsible for issuing and validating access tokens for the sign
    service.

    Only one token can be valid at the same time for a specific document.

    The issued token is only valid for a specific document version and
    cannot be used for other documents
    """

    ANNOTATIONS_KEY = 'sign_token'
    TTL = 3600 * 24 * 30  # one month

    def __init__(self, context):
        self.context = context
        self.annotations = IAnnotations(self.context)

    def issue_token(self):
        token = create_access_token('<sign-service>', self._get_token_scope())
        self._set_token(token)
        return token

    def validate_token(self, token):
        if not token or token != self._get_token():
            raise InvalidToken()

        if not validate_access_token(token, self._get_token_scope(), ttl=self.TTL):
            raise InvalidToken()

        return True

    def invalidate_token(self):
        self.annotations[self.ANNOTATIONS_KEY] = None

    def _get_token_scope(self):
        with elevated_privileges():
            return '{}-{}'.format(IUUID(self.context),
                                  self.context.get_current_version_id())

    def _set_token(self, token):
        self.annotations[self.ANNOTATIONS_KEY] = token

    def _get_token(self):
        return self.annotations.get(self.ANNOTATIONS_KEY)


class InvalidToken(Exception):
    """Token validation failed.
    """
