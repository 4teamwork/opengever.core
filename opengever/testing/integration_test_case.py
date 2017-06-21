from AccessControl import getSecurityManager
from opengever.core.testing import OPENGEVER_INTEGRATION_TESTING
from opengever.testing.helpers import flatten_content_lookup_table
from plone import api
from plone.app.testing import login
from unittest2 import TestCase


"""The CONTENT_LOOKUP_TABLE is used for looking up objects when accessed as
attribute in a test.
In order to keep things organized and paths short, the lookup table is defined
recursively.
"""
CONTENT_LOOKUP_TABLE = flatten_content_lookup_table({
    'repository_root': 'ordnungssystem',
    'branch_repository': 'ordnungssystem/fuhrung',

    'leaf_repository': ('ordnungssystem/fuhrung/vertrage-und-vereinbarungen', {
        'dossier':  ('dossier-1', {
            'subdossier': 'dossier-2'}),
        'archive_dossier': 'dossier-3'}),

    'committee': 'opengever-meeting-committeecontainer/committee-1',
    'committee_container': 'opengever-meeting-committeecontainer',

    'templates': ('vorlagen', {
        'sablon_template': 'document-1',
    }),
})


USER_LOOKUP_TABLE = {
    'administrator': 'nicole.kohler',
    'dossier_responsible': 'robert.ziegler',
    'regular_user': 'kathi.barfuss',
}


class IntegrationTestCase(TestCase):
    layer = OPENGEVER_INTEGRATION_TESTING

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        self.login(self.regular_user)

    def login(self, user):
        """Login a user by passing in the user object.
        Common users are available through the USER_LOOKUP_TABLE.

        Example:
        >>> self.login(self.dossier_responsible)
        """
        login(self.portal, user.getId())

    def __getattr__(self, name):
        """Make it possible to access objects from the content lookup table
        directly with attribute access on the test case.
        """
        if name in CONTENT_LOOKUP_TABLE:
            path = CONTENT_LOOKUP_TABLE[name]
            locals()['__traceback_info__'] = {
                'path': path,
                'current user': getSecurityManager().getUser()}
            return self.portal.restrictedTraverse(path)

        if name in USER_LOOKUP_TABLE:
            return api.user.get(USER_LOOKUP_TABLE[name])

        return self.__getattribute__(name)
