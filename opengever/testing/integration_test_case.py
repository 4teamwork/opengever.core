from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from contextlib import contextmanager
from ftw.flamegraph import flamegraph
from functools import wraps
from opengever.core.testing import OPENGEVER_INTEGRATION_TESTING
from plone import api
from plone.app.testing import login
from plone.app.testing import SITE_OWNER_NAME
from time import clock
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
        self._start_time = clock()
        self._max_duration = 3000

    def tearDown(self):
        super(IntegrationTestCase, self).tearDown()
        duration = (clock() - self._start_time) * 1000
        self.assertLess(
            duration, self._max_duration,
            'The test took to long. It should not take longer'' than {} ms.'
            ' Use the @IntegrationTestCase.open_flamegraph decorator for'
            ' investigating what you can optimize.'.format(self._max_duration))

    @staticmethod
    def im_sorry_this_test_is_slow(expected_duration, reason):
        """If you cannot optimize a test to meet the speed limits but you
        believe that the test is so important that it is an exception to the
        speed limit, you can use this decorator for increasing the limit
        for a certain test, providing a good reason as string why you think this
        exception is reasonable.

        Example:

        @IntegrationTestCase.im_sorry_this_test_is_slow(
            5000,  # new limit in milliseconds
            'This test tests a critical business feature and must build 10 objects'
        )
        def test_critical_feature(self):
            pass
        """
        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                self._max_duration = expected_duration
                return func(self, *args, **kwargs)
            return wrapper
        return decorator

    @staticmethod
    def open_flamegraph(func):
        """Test decorator for opening a flamegraph for creating a flamegraph of
        the decorated test and opening it in the default browser using OS X's
        "open" command.

        Example:

        @IntegrationTestCase.open_flamegraph
        def test_critical_feature(self):
            pass

        """
        return flamegraph(open_svg=True)(func)

    def login(self, user, browser=None):
        """Login a user by passing in the user object.
        Common users are available through the USER_LOOKUP_TABLE.

        Log in security manager and browser:
        >>> self.login(self.dossier_responsible, browser)
        Log in only security manager:
        >>> self.login(self.dossier_responsible)

        The method may also be used used as context manager, ensuring that
        after leaving the same user is logged in as before.
        """

        if hasattr(user, 'getId'):
            userid = user.getId()
        else:
            userid = user

        security_manager = getSecurityManager()
        if userid == SITE_OWNER_NAME:
            login(self.layer['app'], userid)
        else:
            login(self.portal, userid)

        if browser is not None:
            browser_auth_headers = filter(
                lambda item: item[0] == 'Authorization',
                browser.session_headers)
            browser.login(userid)

        @contextmanager
        def login_context_manager():
            try:
                yield
            finally:
                setSecurityManager(security_manager)
                if browser is not None:
                    browser.clear_request_header('Authorization')
                    [browser.append_request_header(name, value)
                     for (name, value) in browser_auth_headers]

        return login_context_manager()

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

    def get_catalog_indexdata(self, obj):
        """Return the catalog index data for an object as dict.
        """
        catalog = api.portal.get_tool('portal_catalog')
        rid = catalog.getrid('/'.join(obj.getPhysicalPath()))
        return catalog.getIndexDataForRID(rid)

    def get_catalog_metadata(self, obj):
        """Return the catalog metadata for an object as dict.
        """
        catalog = api.portal.get_tool('portal_catalog')
        rid = catalog.getrid('/'.join(obj.getPhysicalPath()))
        return catalog.getMetadataForRID(rid)
