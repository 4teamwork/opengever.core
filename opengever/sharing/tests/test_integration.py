from opengever.core.testing import OPENGEVER_FUNCTIONAL_TESTING
from opengever.sharing.browser.sharing import OpengeverSharingView
from opengever.sharing.interfaces import ILocalRolesAcquisitionActivated
from opengever.sharing.interfaces import ILocalRolesAcquisitionBlocked
from opengever.sharing.interfaces import ILocalRolesModified
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from plone.app.testing import setRoles, TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.testing.z2 import Browser
from zope.component import provideHandler
import transaction


class TestOpengeverSharingIntegration(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_TESTING

    def setUp(self):
        """ Set up test environment
        """
        super(TestOpengeverSharingIntegration, self).setUp()
        self.grant('Manager')

        self.request = self.layer['request']
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

            def mock_handler(self, event):
                self.event_history.append(event, )

            def last_event(self):
                return self.event_history[-1]

        self.mock_event = MockEvent()

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

    def test_sharing_views(self):
        """ Test Integration of opengever.sharing
        """

        # We just test to open the views because the rest is tested
        # in other packages
        self.browser.open('%s/@@sharing' % self.dossier.absolute_url())
        self.browser.open(
            '%s/@@tabbedview_view-sharing' % self.dossier.absolute_url())

    def _check_roles(self, expect, roles):
        """ Base method to check the received roles
        """
        # Check the roles and sort order
        for role in roles:
            self.assertTrue(role.get('id') in expect)
            expect.remove(role.get('id'))

        self.assertTrue(len(expect) == 0)

        # Reset the roles
        setRoles(
            self.portal, TEST_USER_ID, ['Manager', 'Contributor', 'Editor'])


    def test_available_roles(self):
        """ Test available roles if we are reader and owner on a context
        providing IDossier of sharing
        """
        setRoles(self.portal, TEST_USER_ID, ['Reader', 'Role Manager'])
        expect = [
            u'Reader',
            u'Editor',
            u'Contributor',
            u'Reviewer',
            u'Publisher',]
        self._check_roles(expect, self.view_dossier.available_roles())

    def test_manageable_roles_with_reader_and_owner(self):
        """ Test manageable roles if we are reader and owner on a context
        providing IDossier of sharing
        """
        setRoles(self.portal, TEST_USER_ID, ['Reader', 'Role Manager'])
        expect = [
            u'Reader',
            u'Editor',
            u'Contributor',
            u'Reviewer',
            u'Publisher',
            u'Administrator', ]
        self._check_roles(expect, self.view_dossier.roles())

    def test_info_tab_roles(self):
        """ Test the roles displayed in the info tab on a context
        providing IDossier of sharing
        """
        setRoles(self.portal, TEST_USER_ID, ['Reader', 'Role Manager'])
        expect = [
            u'Reader',
            u'Editor',
            u'Contributor',
            u'Reviewer',
            u'Publisher',
            u'Administrator', ]
        self._check_roles(expect, self.view_dossier.roles(check_permission=False))


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
        self.view_dossier.update_inherit(False, reindex=False)
        last_event = self.mock_event.last_event()
        self.assertTrue(ILocalRolesAcquisitionBlocked.providedBy(last_event))
        self.assertEquals(last_event.object, self.dossier)

        # we disable it again,it shouldn't fire a event because nothing changed
        self.view_dossier.update_inherit(False, reindex=False)
        self.assertEquals(last_event, self.mock_event.last_event())

        # # We enable locale role aquisition on dossier
        self.view_dossier.update_inherit(True, reindex=False)
        # and check the fired event
        last_event = self.mock_event.last_event()
        self.assertTrue(ILocalRolesAcquisitionActivated.providedBy(last_event))
        self.assertEquals(last_event.object, self.dossier)

        # we disable it again,it shouldn't fire a event because nothing changed
        self.view_dossier.update_inherit(True, reindex=False)
        self.assertEquals(last_event, self.mock_event.last_event())

    def test_update_role_settings(self):
        """ Test update_role_settings method
        """
        # Mock event handler
        provideHandler(
            factory=self.mock_event.mock_handler,
            adapts=[ILocalRolesModified, ], )

        # If nothing has changed it needs to be reported accordingly
        changed = self.view_repo.update_role_settings([], False)
        self.assertFalse(changed)

        # We try to add the new local role 'publisher'
        new_settings = \
            [{'type': 'user', 'id': 'test_user_1_', 'roles': ['Publisher']}, ]

        changed = self.view_repo.update_role_settings(new_settings, False)
        self.assertTrue(changed)

        last_event = self.mock_event.last_event()
        # check the event type
        self.assertTrue(ILocalRolesModified.providedBy(last_event))
        # check the event context
        self.assertEquals(last_event.object, self.repo)
        # check the stored localroles
        self.assertEquals(last_event.old_local_roles,
                          {'test_user_1_': ('Owner',)})
        self.assertEquals(last_event.new_local_roles,
                          (('test_user_1_', ('Owner', 'Publisher')),))

        # now we remvove the local role 'publisher'
        new_settings = \
            [{'type': 'user', 'id': 'test_user_1_', 'roles': []}, ]

        changed = self.view_repo.update_role_settings(new_settings, False)
        self.assertTrue(changed)

        # check event attributes
        last_event = self.mock_event.last_event()
        self.assertTrue(ILocalRolesModified.providedBy(last_event))
        self.assertEquals(last_event.object, self.repo)
        self.assertEquals(last_event.old_local_roles,
                          {'test_user_1_': ('Owner', 'Publisher')})
        self.assertTrue(
            last_event.new_local_roles == (('test_user_1_', ('Owner',)),))
