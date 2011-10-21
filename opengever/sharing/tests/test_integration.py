from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from opengever.sharing.testing import OPENGEVER_SHARING_INTEGRATION_TESTING
from opengever.sharing.browser.sharing import OpengeverSharingView
from plone.dexterity.utils import createContentInContainer
from plone.testing.z2 import Browser
import unittest2 as unittest
from plone.app.testing import setRoles, TEST_USER_ID
import transaction
from zope.component import provideHandler
from opengever.sharing.interfaces import \
    ILocalRolesAcquisitionBlocked, ILocalRolesAcquisitionActivated, \
    ILocalRolesModified
from opengever.sharing.events import \
    LocalRolesAcquisitionActivated, LocalRolesAcquisitionBlocked, \
    LocalRolesModified


class TestOpengeverSharingIntegration(unittest.TestCase):

    layer = OPENGEVER_SHARING_INTEGRATION_TESTING

    def setUp(self):
        """ Set up test environment
        """

        self.request = self.layer['request']
        self.portal = self.layer['portal']
        self.browser = self.get_browser()

        # Setup minimal repo with one dossier
        self.repo_root = createContentInContainer(
            self.portal, 'opengever.repository.repositoryroot', 'root')
        self.repo = createContentInContainer(
            self.repo_root, 'opengever.repository.repositoryfolder', 'r1')
        self.dossier = createContentInContainer(
            self.repo, 'opengever.dossier.businesscasedossier', 'd1')
        transaction.commit()

        # Get the sharing-view of repo and dossier
        self.view_repo = OpengeverSharingView(self.repo, self.request)
        self.view_dossier = OpengeverSharingView(self.dossier, self.request)

        # Event class to look for fired events
        class MockEvent(object):

            # History: [[interface, context], ]
            event_history = []

            def mock_handler(self, handler):
                self.event_history.append([handler, handler.object])

        self.mock_event = MockEvent()

    def test_available_roles_with_manager(self):
        """ Test available roles if we are manager on a context providing
        IDossier of sharing
        """
        setRoles(self.portal, TEST_USER_ID, ['Manager', ])
        expect = [
            u'Reader',
            u'Editor',
            u'Contributor',
            u'Reviewer',
            u'Publisher',
            u'Administrator', ]

        self.base_available_roles(expect)

    def test_available_roles_with_reader_and_owner(self):
        """ Test available roles if we are reader and owner on a context
        providing IDossier of sharing
        """
        setRoles(self.portal, TEST_USER_ID, ['Reader', ])
        expect = [u'Reader', u'Editor', u'Contributor', ]

        self.base_available_roles(expect)

    def base_available_roles(self, expect):
        """ Base method to check the received roles
        """

        roles = self.view_dossier.available_roles()

        # Check the roles and sort order

        for role in roles:
            self.assertTrue(role.get('id') in expect)
            expect.remove(role.get('id'))

        self.assertTrue(len(expect) == 0)

        # Reset the roles
        setRoles(
            self.portal, TEST_USER_ID, ['Manager', 'Contributor', 'Editor'])

    def test_integration_dossier_events(self):
        """ Test Integration of opengever.sharing
        """

        self.request = self.layer['request']
        self.portal = self.layer['portal']
        self.browser = self.get_browser()

        # Setup minimal repo with one dossier
        self.repo_root = createContentInContainer(
            self.portal, 'opengever.repository.repositoryroot', 'root')
        self.repo = createContentInContainer(
            self.repo_root, 'opengever.repository.repositoryfolder', 'r1')
        self.dossier = createContentInContainer(
            self.repo, 'opengever.dossier.businesscasedossier', 'd1')

        transaction.commit()

        # Get the sharing-view of repo and dossier
        self.view_repo = OpengeverSharingView(self.repo, self.request)
        self.view_dossier = OpengeverSharingView(self.dossier, self.request)

        # Event class to look for fired events
        class MockEvent(object):

            # History: [[interface, context], ]
            event_history = []

            def mock_handler(self, handler):
                self.event_history.append([handler, handler.object])

        self.mock_event = MockEvent()

    def test_sharing_views(self):
        """ Test Integration of opengever.sharing
        """

        # We just test to open the views because the rest is tested
        # in other packages
        self.browser.open('%s/@@sharing' % self.dossier.absolute_url())
        self.browser.open(
            '%s/@@tabbedview_view-sharing' % self.dossier.absolute_url())

    def test_update_inherit(self):
        """ tests update inherit method

        We are owner of the portal, with inheritance we are also owner of
        the repo and dossier. If we disable role aquisition on context,
        we lose the role 'owner' on the context
        """

        # Mock event handlers
        provideHandler(
            factory=self.mock_event.mock_handler,
            adapts=[ILocalRolesAcquisitionBlocked, ], )
        provideHandler(
            factory=self.mock_event.mock_handler,
            adapts=[ILocalRolesAcquisitionActivated, ], )

        # We disable locale role aquisition on dossier
        self.base_update_inherit(self.view_dossier, self.dossier, False)

        # We disable locale role aquisition on repo.
        # The journalentry is on the next repo_root object or plone
        # siteroot. In our case we have a repo object, so we have
        # to check the repo_root
        self.base_update_inherit(self.view_repo, self.repo, False)

        # We enable locale role aquisition on dossier
        self.base_update_inherit(self.view_dossier, self.dossier, True)

        # And again on the repo
        self.base_update_inherit(self.view_repo, self.repo, True)

    def base_update_inherit(self, view, context, status, reindex=False):
        """ Base method to call update_inherit mehtod
        """
        # Get the number of fired events before the update
        events_before = len(self.mock_event.event_history)

        # Update inherit
        view.update_inherit(status, reindex)

        # Get the fired event
        event = status and LocalRolesAcquisitionActivated or \
            LocalRolesAcquisitionBlocked

        # Check the result of the function
        self.check_event_history(events_before, event, context)

    def test_update_role_settings(self):
        """ Test update_role_settings method
        """
        # Mock event handler
        provideHandler(
            factory=self.mock_event.mock_handler,
            adapts=[ILocalRolesModified, ], )

        # We try to add the new local role 'publisher'
        new_settings = \
            [{'type': 'user', 'id': 'test_user_1_', 'roles': ['Publisher']}, ]

        self.base_update_role_settings(
            self.view_dossier, self.dossier, new_settings)

        self.base_update_role_settings(
            self.view_repo, self.repo, new_settings)

        # We try to remove the new local role 'publisher'
        new_settings = \
            [{'type': 'user', 'id': 'test_user_1_', 'roles': []}, ]

        self.base_update_role_settings(
            self.view_dossier, self.dossier, new_settings)

        self.base_update_role_settings(
            self.view_repo, self.repo, new_settings)

    def base_update_role_settings(
        self, view, context, settings, reindex=False):
        """ Base method to call update_role_settings method
        """
        # Get the number of fired events before the update
        events_before = len(self.mock_event.event_history)

        # Update role_settings
        view.update_role_settings(settings, reindex)

        # Check the result of the function
        self.check_event_history(events_before, LocalRolesModified, context)

    def check_event_history(self, len_before, event, context):
        """ Check the event history of the dummy event class
        """

        # We need one more entry than before
        self.assertTrue(
            len_before+1 == len(self.mock_event.event_history))

        # The right event must be called
        self.assertTrue(
            self.mock_event.event_history[-1][0].__class__ == event)

        # The right context must fire the event
        self.assertTrue(
            self.mock_event.event_history[-1][1] == context)

    def get_browser(self):
        """Return logged in browser
        """
        # Create browser an login
        portal_url = self.layer['portal'].absolute_url()
        browser = Browser(self.layer['app'])
        browser.open('%s/login_form' % portal_url)
        browser.getControl(name='__ac_name').value = TEST_USER_NAME
        browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
        browser.getControl(name='submit').click()

        # Check login
        self.assertNotEquals('__ac_name' in browser.contents, True)
        self.assertNotEquals('__ac_password' in browser.contents, True)

        return browser
