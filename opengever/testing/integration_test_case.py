from AccessControl import getSecurityManager
from opengever.core.testing import OPENGEVER_INTEGRATION_TESTING
from plone import api
from plone.app.testing import login
from plone.app.testing import SITE_OWNER_NAME
from unittest2 import TestCase


FEATURE_FLAGS = {
    'meeting': 'opengever.meeting.interfaces.IMeetingSettings.is_feature_enabled',
    'dossiertemplate': ('opengever.dossier.dossiertemplate'
                        '.interfaces.IDossierTemplateSettings.is_feature_enabled'),
}


class IntegrationTestCase(TestCase):
    layer = OPENGEVER_INTEGRATION_TESTING
    features = ()

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        map(self.activate_feature, self.features)
        self.login(self.regular_user)

    def login(self, user, browser=None):
        """Login a user by passing in the user object.
        Common users are available through the USER_LOOKUP_TABLE.

        Log in security manager and browser:
        >>> self.login(self.dossier_responsible, browser)
        Log in only security manager:
        >>> self.login(self.dossier_responsible)
        """
        if hasattr(user, 'getId'):
            userid = user.getId()
        else:
            userid = user

        if userid == SITE_OWNER_NAME:
            login(self.layer['app'], userid)
        else:
            login(self.portal, userid)

        if browser is not None:
            browser.login(userid)

    def activate_feature(self, feature):
        """Activate a feature flag.
        """
        api.portal.set_registry_record(FEATURE_FLAGS[feature], True)

    def __getattr__(self, name):
        """Make it possible to access objects from the content lookup table
        directly with attribute access on the test case.
        """
        obj = self._lookup_from_table(name)
        if obj is not None:
            return obj
        else:
            return self.__getattribute__(name)

    def _lookup_from_table(self, name):
        """This method helps to look up persistent objects or user objects which
        were created in the fixture and registered there with a name.
        """
        try:
            table = self.layer['fixture_lookup_table']
        except KeyError:
            # The layer has not yet set up the fixture.
            return None
        if name not in table:
            return None

        type_, value = table[name]
        if type_ == 'object':
            locals()['__traceback_info__'] = {
                'path': value,
                'current user': getSecurityManager().getUser()}
            return self.portal.restrictedTraverse(value)

        elif type_ == 'user':
            return api.user.get(value)

        else:
            raise ValueError('Unsupport lookup entry type {!r}'.format(type_))
