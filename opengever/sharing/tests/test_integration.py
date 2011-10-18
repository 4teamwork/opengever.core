from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD, TEST_USER_ID
from opengever.sharing.testing import OPENGEVER_SHARING_INTEGRATION_TESTING
from opengever.sharing.browser.sharing import OpengeverSharingView
from plone.dexterity.utils import createContentInContainer
from plone.testing.z2 import Browser
import unittest2 as unittest
import transaction
from DateTime import DateTime
from zope.annotation.interfaces import IAnnotations
from ftw.journal.config import JOURNAL_ENTRIES_ANNOTATIONS_KEY


class TestOpengeverJournalIntegration(unittest.TestCase):

    layer = OPENGEVER_SHARING_INTEGRATION_TESTING

    def test_sharing_views(self):
        """ Test Integration of opengever.sharing
        """
        portal = self.layer['portal']

        dossier = createContentInContainer(
            portal, 'opengever.dossier.businesscasedossier', 'd1')

        transaction.commit()
        browser = self.get_browser()

        # We just test to open the views because the rest is tested
        # in other packages
        browser.open('%s/@@sharing' % dossier.absolute_url())
        browser.open('%s/@@tabbedview_view-sharing' % dossier.absolute_url())

    def test_update_inherit(self):

        request = self.layer['request']
        portal = self.layer['portal']

        # We are owner of the portal, with inheritance we are also owner of
        # the repo and dossier. If we disable role aquisition on context, we lose the
        # role 'owner' on the context
        repo = createContentInContainer(
            portal, 'opengever.repository.repositoryfolder', 'r1')
        dossier = createContentInContainer(
            repo, 'opengever.dossier.businesscasedossier', 'd1')

        view = OpengeverSharingView(dossier, request)

        # We disable locale role aquisition on dossier
        view.update_inherit(status=False, reindex=False)

        self.check_annotation(
            dossier,
            'Local roles Aquisition Blocked',
            'label_local_roles_acquisition_blocked')

        # We disable locale role aquisition on repo.
        view.update_inherit(status=False, reindex=False)

        self.check_annotation(
            repo,
            'Local roles Aquisition Blocked',
            'label_local_roles_acquisition_blocked')

        # We enable locale role aquisition on dossier
        view.update_inherit(status=True, reindex=False)

        self.check_annotation(
            dossier,
            'Local roles Aquisition Activated',
            'label_local_roles_acquisition_activated')

    def test_update_role_settings(self):
        pass

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

    def check_annotation(self,
                         obj,
                         action_type='',
                         action_title='',
                         actor=TEST_USER_ID,
                         comment='',
                         check_entry=-1, ):
        """ Check the annotations for the right entries.
        """
        time = DateTime().Date()
        import pdb; pdb.set_trace( )
        journal = IAnnotations(
            obj, JOURNAL_ENTRIES_ANNOTATIONS_KEY).get(
                JOURNAL_ENTRIES_ANNOTATIONS_KEY)[check_entry]

        self.assertTrue(comment == journal.get('comments'))
        self.assertTrue(actor == journal.get('actor'))
        self.assertTrue(time == journal.get('time').Date())
        self.assertTrue(action_type == journal.get('action').get('type'))
        self.assertTrue(action_title == journal.get('action').get('title'))
