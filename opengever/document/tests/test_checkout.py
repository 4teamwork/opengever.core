from AccessControl import Unauthorized
from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import assert_message
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from ftw.testing import freeze
from opengever.base.interfaces import IRedirector
from opengever.document.checkout.manager import CHECKIN_CHECKOUT_ANNOTATIONS_KEY
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.document.versioner import Versioner
from opengever.journal.handlers import DOCUMENT_CHECKED_IN
from opengever.officeconnector.helpers import create_oc_url
from opengever.officeconnector.interfaces import IOfficeConnectorSettings
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2brain
from opengever.testing.helpers import create_document_version
from opengever.trash.trash import Trasher
from plone import api
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.locking.interfaces import IRefreshableLockable
from plone.namedfile.file import NamedBlobFile
from plone.protect import createToken
from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
import jwt
import transaction


class TestCheckinIntegration(IntegrationTestCase):

    def test_manager_can_force_checkin(self):
        self.login(self.regular_user)
        manager = getMultiAdapter((self.document, self.portal.REQUEST),
                                  ICheckinCheckoutManager)
        manager.checkout()
        self.assertEqual(self.regular_user.getName(),
                         manager.get_checked_out_by())

        # Dossier Manager can't force checkin
        self.login(self.dossier_manager)
        with self.assertRaises(Unauthorized):
            manager.checkin(comment="Force checkin")

        # Dossier Responsible can't force checkin
        self.login(self.dossier_responsible)
        with self.assertRaises(Unauthorized):
            manager.checkin(comment="Force checkin")

        # Administrator can force checkin
        self.login(self.administrator)
        manager.checkin(comment="Force checkin")
        self.assertIsNone(manager.get_checked_out_by())

    def test_force_checkin_clears_lock(self):
        self.login(self.regular_user)
        manager = getMultiAdapter((self.document, self.portal.REQUEST),
                                  ICheckinCheckoutManager)
        manager.checkout()
        self.assertFalse(IRefreshableLockable(self.document).locked())
        IRefreshableLockable(self.document).lock()
        self.assertTrue(IRefreshableLockable(self.document).locked())

        self.login(self.administrator)
        manager.checkin(comment="Force checkin")
        self.assertFalse(IRefreshableLockable(self.document).locked())

    def test_collaborative_checkin(self):
        self.login(self.regular_user)
        manager = getMultiAdapter((self.document, self.portal.REQUEST),
                                  ICheckinCheckoutManager)

        manager.checkout(collaborative=True)
        self.assertEqual(self.regular_user.getId(),
                         manager.get_checked_out_by())

        # List of collaborators starts out with the user that initially
        # checked out the document
        self.assertEqual([self.regular_user.getId()],
                         manager.get_collaborators())

        # Other collaborator can checkin
        manager.add_collaborator(self.dossier_responsible.getId())
        self.assertEqual(
            [self.regular_user.getId(), self.dossier_responsible.getId()],
            manager.get_collaborators())

        self.login(self.dossier_responsible)
        manager.checkin(collaborative=True)
        self.assertIsNone(manager.get_checked_out_by())

    def test_collaborative_checkin_only_allowed_for_other_collaborators(self):
        self.login(self.regular_user)
        manager = getMultiAdapter((self.document, self.portal.REQUEST),
                                  ICheckinCheckoutManager)

        manager.checkout(collaborative=True)
        self.assertEqual(self.regular_user.getId(),
                         manager.get_checked_out_by())

        # This user is not a collaborator
        self.login(self.dossier_responsible)

        self.assertFalse(manager.is_checkin_allowed())
        with self.assertRaises(Unauthorized):
            manager.checkin(collaborative=True)

    def test_collaborative_checkout_can_only_be_checked_in_collaboratively(self):
        self.login(self.regular_user)
        manager = getMultiAdapter((self.document, self.portal.REQUEST),
                                  ICheckinCheckoutManager)

        manager.checkout(collaborative=True)
        manager.add_collaborator(self.dossier_responsible.getId())
        self.assertEqual(self.regular_user.getId(),
                         manager.get_checked_out_by())

        # Regular checkin is not allowed
        self.assertFalse(manager.is_checkin_allowed())
        with self.assertRaises(Unauthorized):
            manager.checkin()

    def test_collaborators_are_cleared_after_checkin(self):
        self.login(self.regular_user)
        manager = getMultiAdapter((self.document, self.portal.REQUEST),
                                  ICheckinCheckoutManager)

        manager.checkout(collaborative=True)
        manager.add_collaborator(self.dossier_responsible.getId())
        self.assertEqual(
            [self.regular_user.getId(), self.dossier_responsible.getId()],
            manager.get_collaborators())
        self.assertTrue(manager.is_collaborative_checkout())

        # List of collaborators should be cleared on checkin
        manager.checkin(collaborative=True)
        self.assertEqual([], manager.get_collaborators())
        self.assertFalse(manager.is_collaborative_checkout())
        self.assertIsNone(manager.get_checked_out_by())

    def test_collaborative_checkout_can_be_force_checked_in(self):
        self.login(self.regular_user)
        manager = getMultiAdapter((self.document, self.portal.REQUEST),
                                  ICheckinCheckoutManager)

        manager.checkout(collaborative=True)
        manager.add_collaborator(self.dossier_responsible.getId())
        self.assertEqual(self.regular_user.getId(),
                         manager.get_checked_out_by())

        # Force checkin is still allowed
        self.login(self.administrator)
        self.assertTrue(manager.is_checkin_allowed())
        manager.checkin()
        self.assertIsNone(manager.get_checked_out_by())
        self.assertEqual([], manager.get_collaborators())

    def test_collaborators_get_written_to_journal_and_version_comments(self):
        self.login(self.regular_user)
        manager = getMultiAdapter((self.document, self.portal.REQUEST),
                                  ICheckinCheckoutManager)

        manager.checkout(collaborative=True)
        manager.add_collaborator(self.dossier_responsible.getId())

        manager.checkin(collaborative=True)

        collaborator_note = (u'Collaborators: '
                             u'B\xe4rfuss K\xe4thi (kathi.barfuss), '
                             u'Ziegler Robert (robert.ziegler)')

        version_metadata = Versioner(self.document).get_version_metadata(0)
        version_comment = version_metadata['sys_metadata']['comment']
        self.assertEqual(collaborator_note, version_comment)

        self.assert_journal_entry(
            self.document,
            DOCUMENT_CHECKED_IN,
            u'Document checked in',
            comment=collaborator_note.encode('utf-8'),
        )


class TestCheckin(FunctionalTestCase):
    """Tests for the checkin functionality."""

    document_date = date(2014, 1, 1)

    def setUp(self):
        super(TestCheckin, self).setUp()
        self.dossier = create(Builder('dossier'))

        self.document = create(Builder('document')
                               .with_dummy_content()
                               .having(document_date=self.document_date)
                               .within(self.dossier)
                               .checked_out())

        self.manager = self.get_manager(self.document)

    def get_manager(self, document):
        return getMultiAdapter(
            (document, self.portal.REQUEST), ICheckinCheckoutManager)

    def test_annotations_key_is_cleared(self):
        annotations = IAnnotations(self.document)
        self.assertEquals(
            TEST_USER_ID, annotations.get(CHECKIN_CHECKOUT_ANNOTATIONS_KEY))

        self.manager.checkin()

        self.assertEquals(
            None, annotations.get(CHECKIN_CHECKOUT_ANNOTATIONS_KEY))

    def test_new_version_is_created(self):
        self.document.file = NamedBlobFile(
            data='New conent', filename=u'test.txt')

        self.manager.checkin()

        repo_tool = api.portal.get_tool('portal_repository')
        history = repo_tool.getHistory(self.document)
        self.assertEquals(2, len(history))

    def test_clear_locks(self):
        IRefreshableLockable(self.document).lock()
        self.assertTrue(IRefreshableLockable(self.document).locked())

        self.manager.checkin()
        self.assertFalse(IRefreshableLockable(self.document).locked())

    def test_document_date_is_not_updated_when_checked_in(self):
        self.manager.checkin()
        self.assertEquals(self.document_date, self.document.document_date)


class TestReverting(FunctionalTestCase):
    """Tests for reverting documents to older revisions."""

    document_date = date(2014, 1, 1)

    def setUp(self):
        super(TestReverting, self).setUp()
        self.dossier = create(Builder('dossier'))
        self.document = create(Builder('document')
                               .having(document_date=self.document_date)
                               .within(self.dossier)
                               .attach_file_containing(
                                   u"INITIAL VERSION DATA", u"somefile.txt"))

        # trigger initial version creation
        self.document.file = NamedBlobFile(
            data='New conent', filename=u'test.txt')

        create_document_version(self.document, 1)
        create_document_version(self.document, 2)
        transaction.commit()

        self.manager = getMultiAdapter(
            (self.document, self.portal.REQUEST), ICheckinCheckoutManager)

    def test_creates_new_version_with_same_data(self):
        self.manager.revert_to_version(2)

        repo_tool = api.portal.get_tool('portal_repository')
        version2 = repo_tool.retrieve(self.document, 2)

        self.assertEquals(4, len(repo_tool.getHistory(self.document)))
        self.assertEqual(self.document.file.data, version2.object.file.data)
        self.assertEquals(u'Reverted file to version 2.',
                          repo_tool.retrieve(self.document, 3).comment)

    def test_creates_a_new_blob_instance(self):
        self.manager.revert_to_version(2)

        repo_tool = api.portal.get_tool('portal_repository')
        version2 = repo_tool.retrieve(self.document, 2)

        self.assertNotEqual(
            self.document.file._blob, version2.object.file._blob)
        self.assertNotEqual(self.document.file, version2.object.file)

    def test_reverting_to_older_version_does_not_revert_metadata(self):
        self.assertEqual(u'Testdokum\xe4nt', self.document.title)

        self.document.title = "New title"
        create_document_version(self.document, 3)

        # Plone retrieves previous version of the whole object
        # including metadata
        repo_tool = api.portal.get_tool('portal_repository')
        version4 = repo_tool.retrieve(self.document, 3)
        self.assertEqual("New title", version4.object.title)
        version3 = repo_tool.retrieve(self.document, 2)
        self.assertEqual(u'Testdokum\xe4nt', version3.object.title)

        # GEVER's revert only retrieves the file
        self.manager.revert_to_version(2)
        self.assertEqual("New title", self.document.title)

    def test_revert_disallowed_for_unprivileded_user(self):
        self.grant('Authenticated')
        self.assertFalse(self.manager.is_revert_allowed())

    def test_revert_disallowed_when_checked_out(self):
        self.manager.checkout()
        self.assertFalse(self.manager.is_revert_allowed())

    def test_revert_disallowed_when_locked(self):
        IRefreshableLockable(self.document).lock()
        self.assertFalse(self.manager.is_revert_allowed())

    def test_revert_disallowed_when_trashed(self):
        Trasher(self.document).trash()
        self.assertFalse(self.manager.is_revert_allowed())

    def test_manager_raises_unauthorized_when_reverting_disallowed(self):
        self.manager.checkout()

        with self.assertRaises(Unauthorized):
            self.manager.revert_to_version(2)

    @browsing
    def test_reverting_with_revert_link_in_versions_tab(self, browser):
        browser.login().open(self.document, view='tabbedview_view-versions')
        listing = browser.css('.listing').first

        second_row = listing.css('tr')[2]
        self.assertIn('This is Version 1', second_row.text)

        revert_link = second_row.css('td a')[-1]
        revert_link.click()

        self.assertEquals(['Reverted file to version 1.'], info_messages())
        self.assertEquals('VERSION 1 DATA', self.document.file.data)

    @browsing
    def test_revert_link_discreet_when_reverting_disallowed(self, browser):
        self.manager.checkout()
        transaction.commit()

        browser.login().open(self.document, view='tabbedview_view-versions')
        self.assertEqual('Revert', browser.css('span.discreet').first.text)

    @browsing
    def test_browser_revert_view_raises_unauthorized_when_revert_disallowed(self, browser):
        self.manager.checkout()
        transaction.commit()

        with browser.expect_unauthorized():
            browser.login().open(
                self.document,
                view='revert-file-to-version?version_id=2&_authenticator={}'
                .format(createToken()))


class TestManagerHelpers(FunctionalTestCase):
    """Tests for the checkin-checkout manager helper functions."""

    def get_manager(self, document):
        return getMultiAdapter(
            (document, self.portal.REQUEST), ICheckinCheckoutManager)

    def test_is_checked_out_by_current_user(self):
        doc = create(Builder('document').checked_out())
        self.assertTrue(self.get_manager(doc).is_checked_out_by_current_user())

    def test_is_not_checked_out_by_current_user_when_document_is_checked_out_by_another_user(self):
        doc = create(Builder('document').checked_out_by('hugo.boss'))
        self.assertFalse(
            self.get_manager(doc).is_checked_out_by_current_user())

    def test_is_not_checked_out_when_document_is_checked_in(self):
        doc = create(Builder('document'))
        self.assertFalse(
            self.get_manager(doc).is_checked_out_by_current_user())

    def test_file_upload_is_disallowed_when_document_is_locked(self):
        doc = create(Builder('document').checked_out())
        IRefreshableLockable(doc).lock()

        self.assertFalse(self.get_manager(doc).is_file_upload_allowed())

    def test_file_upload_is_disallowed_when_document_is_checked_out_by_other_user(self):
        doc = create(Builder('document').checked_out_by('hugo.boss'))
        self.assertFalse(self.get_manager(doc).is_file_upload_allowed())

    def test_file_upload_is_disallowed_when_document_is_not_checked_out(self):
        doc = create(Builder('document'))
        self.assertFalse(self.get_manager(doc).is_file_upload_allowed())

    def test_file_upload_is_allowed_when_document_is_checked_out_and_not_locked(self):
        doc = create(Builder('document').checked_out())
        self.assertTrue(self.get_manager(doc).is_file_upload_allowed())

    def test_checkin_permissions_when_document_is_checked_out_by_other_user(self):
        doc = create(Builder('document').checked_out_by('hugo.boss'))
        self.assertFalse(self.get_manager(doc).is_checkin_allowed())
        self.grant('Manager')
        self.assertTrue(self.get_manager(doc).is_checkin_allowed())

        other_user = create(Builder('user').named("Other", "User")
                            .with_roles("Member"))
        self.login(other_user.id)
        self.assertFalse(self.get_manager(doc).is_checkin_allowed())
        doc.aq_parent.manage_permission("opengever.document: Force Checkin",
                                        roles=["Member"], acquire=True)
        self.assertTrue(self.get_manager(doc).is_checkin_allowed())


class TestCheckinCheckoutManager(FunctionalTestCase):
    """Tests for the checkin-checkout manager."""

    def setUp(self):
        super(TestCheckinCheckoutManager, self).setUp()
        self.prepareSession()

        self.repo, self.repo_folder = create(Builder('repository_tree'))

        self.dossier = create(Builder('dossier').within(self.repo_folder))
        self.doc1 = create(
            Builder('document')
            .within(self.dossier)
            .titled(u'Document1')
            .with_dummy_content())
        self.doc2 = create(
            Builder('document')
            .within(self.dossier)
            .titled(u'Document2')
            .with_dummy_content())

    def test_checkout(self):
        view = self.doc1.restrictedTraverse('@@editing_document')()

        self.assertEquals(self.doc1.absolute_url(), view)
        self.assertEquals(
            self.doc1.absolute_url() + '/external_edit',
            IRedirector(self.doc1.REQUEST).get_redirects()[0].get('url'))
        self.assertEquals(TEST_USER_ID,
                          self.get_manager(self.doc1).get_checked_out_by())

    @browsing
    def test_checkout_with_officeconnector_enabled(self, browser):
        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)
        transaction.commit()

        # We cannot freeze time due to the test browser being threaded
        oc_url = create_oc_url(
            self.doc1.REQUEST, self.doc1, {'action': 'checkout'})
        decoded_oc_url = jwt.decode(
            oc_url.split(':')[-1], verify=False, algorithms=('HS256',))

        redirector_js = browser.login().open(
            self.doc1,
            view='checkout_documents'
            '?_authenticator={}&mode=external'
            .format(createToken()),
            ).css('script.redirector')[0].text

        tokens_from_js = [token for token in redirector_js.split("\'")
                          if 'oc:' in token]

        self.assertEqual(3, len(tokens_from_js))

        parsed_oc_url = tokens_from_js[0]
        decoded_parsed_oc_url = jwt.decode(
            parsed_oc_url.split(':')[-1], verify=False, algorithms=('HS256',))

        # Take out the timestamps
        del decoded_oc_url['exp']
        del decoded_parsed_oc_url['exp']

        self.assertEqual(decoded_oc_url, decoded_parsed_oc_url)
        self.assertTrue(self.get_manager(self.doc1).is_checked_out_by_current_user())

    @browsing
    def test_officeconnector_reauth_does_not_checkout(self, browser):
        api.portal.set_registry_record(
            'direct_checkout_and_edit_enabled',
            True,
            interface=IOfficeConnectorSettings)
        transaction.commit()

        # We cannot freeze time due to the test browser being threaded
        oc_url = create_oc_url(
            self.doc1.REQUEST, self.doc1, {'action': 'checkout'})
        decoded_oc_url = jwt.decode(
            oc_url.split(':')[-1], verify=False, algorithms=('HS256',))

        redirector_js = browser.login().open(
            self.doc1,
            view='checkout_documents'
            '?_authenticator={}&mode=external&reauth=1'
            .format(createToken()),
            ).css('script.redirector')[0].text

        tokens_from_js = [token for token in redirector_js.split("\'")
                          if 'oc:' in token]

        self.assertEqual(3, len(tokens_from_js))

        parsed_oc_url = tokens_from_js[0]
        decoded_parsed_oc_url = jwt.decode(
            parsed_oc_url.split(':')[-1], verify=False, algorithms=('HS256',))

        # Take out the timestamps
        del decoded_oc_url['exp']
        del decoded_parsed_oc_url['exp']

        self.assertEqual(decoded_oc_url, decoded_parsed_oc_url)
        self.assertFalse(self.get_manager(self.doc1).is_checked_out_by_current_user())

    def test_cancel(self):
        manager = self.get_manager(self.doc1)
        manager.checkout()

        transaction.commit()
        self.portal.REQUEST['paths'] = [obj2brain(self.doc1).getPath(), ]
        view = self.doc1.restrictedTraverse('cancel_document_checkouts')()

        self.assertEquals(self.doc1.absolute_url(), view)
        self.assertEquals(None, manager.get_checked_out_by())

    def test_bulk_checkout(self):
        self.portal.REQUEST['paths'] = [
            obj2brain(self.doc1).getPath(),
            obj2brain(self.doc2).getPath(),
        ]
        view = self.portal.restrictedTraverse(
            '@@checkout_documents')()
        self.assertEquals('http://nohost/plone#documents', view)

        self.assertEquals(
            TEST_USER_ID, self.get_manager(self.doc1).get_checked_out_by())
        self.assertEquals(
            TEST_USER_ID, self.get_manager(self.doc2).get_checked_out_by())

    def get_manager(self, document):
        return getMultiAdapter(
            (document, self.portal.REQUEST), ICheckinCheckoutManager)


class TestCheckinViews(IntegrationTestCase):
    """Tests for the checkin views."""

    features = (
        '!officeconnector-checkout',
    )

    @browsing
    def test_checkin_anyway_shown_for_locked_documents(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')
        browser.find('Checkout and edit').click()

        browser.open(self.document)
        browser.css('#checkin_with_comment').first.click()
        self.assertEqual(0, len(browser.css('#form-buttons-button_checkin_anyway')))
        self.assertEqual(browser.css('#form-buttons-button_checkin').first.name, 'form.buttons.button_checkin')

        # Lock document
        IRefreshableLockable(self.document).lock()

        browser.open(self.document)
        browser.css('#checkin_with_comment').first.click()
        self.assertEqual(0, len(browser.css('#form-buttons-button_checkin')))
        self.assertEqual(browser.css('#form-buttons-button_checkin_anyway').first.name, 'form.buttons.button_checkin_anyway')

    @browsing
    def test_single_checkin_with_comment(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')
        browser.find('Checkout and edit').click()

        # open checkin form
        browser.open(self.document)
        browser.css('#checkin_with_comment').first.click()

        # fill and submit checkin form
        journal_comment = u'Checkinerino'
        browser.fill({
            u'Journal Comment': journal_comment,
            })

        browser.css('#form-buttons-button_checkin').first.click()

        manager = getMultiAdapter(
            (self.document, self.portal.REQUEST),
            ICheckinCheckoutManager,
            )

        self.assertEquals(None, manager.get_checked_out_by())

        self.assert_journal_entry(
            self.document,
            DOCUMENT_CHECKED_IN,
            u'Document checked in',
            comment=journal_comment,
            )

    @browsing
    def test_single_locked_checkin_with_comment(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')
        browser.find('Checkout and edit').click()

        # Lock document
        IRefreshableLockable(self.document).lock()

        browser.open(self.document)

        # open checkin form
        browser.css('#checkin_with_comment').first.click()

        assert_message(
            ' '.join((
                'This document is currently being worked on.',
                'When you check it in manually you will lose the changes.',
                'Please allow for the process to be finished first.',
                ))
            )

        self.assertIn(
            'Checkin anyway',
            browser.css('#form-buttons-button_checkin_anyway')[0].outerHTML
            )

        self.assertNotIn(
            'Cancel Checkout',
            browser.css('.contentViews a').text
            )

        # fill and submit checkin form
        journal_comment = u'Checkinerino'
        browser.fill({
            u'Journal Comment': journal_comment,
            })

        browser.css('#form-buttons-button_checkin_anyway').first.click()

        manager = getMultiAdapter(
            (self.document, self.portal.REQUEST),
            ICheckinCheckoutManager,
            )

        self.assertEquals(None, manager.get_checked_out_by())

        self.assert_journal_entry(
            self.document,
            DOCUMENT_CHECKED_IN,
            u'Document checked in',
            comment=journal_comment,
            )

    @browsing
    def test_multi_checkin_from_tabbedview_with_comment(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')
        browser.find('Checkout and edit').click()

        browser.open(self.subdocument, view='tabbedview_view-overview')
        browser.find('Checkout and edit').click()

        browser.open(
            self.dossier,
            method='POST',
            data={
                'paths': [
                    obj2brain(self.document).getPath(),
                    obj2brain(self.subdocument).getPath(),
                    ],
                'checkin_documents:method': 1,
                '_authenticator': createToken(),
                },
            )

        # fill and submit checkin form
        journal_comment = u'Checkini'
        browser.fill({
            'Journal Comment': journal_comment,
            })

        browser.css('#form-buttons-button_checkin').first.click()

        for doc in (self.document, self.subdocument, ):
            manager = getMultiAdapter(
                (doc, self.portal.REQUEST),
                ICheckinCheckoutManager,
                )

            self.assertEquals(None, manager.get_checked_out_by())

            self.assert_journal_entry(
                doc,
                DOCUMENT_CHECKED_IN,
                u'Document checked in',
                comment=journal_comment,
                )

    @browsing
    def test_single_checkin_without_comment(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')
        browser.find('Checkout and edit').click()

        browser.open(self.document)

        browser.css('#checkin_without_comment').first.click()

        manager = getMultiAdapter(
            (self.document, self.portal.REQUEST),
            ICheckinCheckoutManager,
            )

        self.assertEquals(None, manager.get_checked_out_by())

        self.assert_journal_entry(
            self.document,
            DOCUMENT_CHECKED_IN,
            u'Document checked in',
            comment='',
            )

    @browsing
    def test_multi_checkin_from_tabbedview_without_comment(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')
        browser.find('Checkout and edit').click()

        browser.open(self.subdocument, view='tabbedview_view-overview')
        browser.find('Checkout and edit').click()

        browser.open(
            self.dossier,
            method='POST',
            data={
                'paths': [
                    obj2brain(self.document).getPath(),
                    obj2brain(self.subdocument).getPath(),
                    ],
                'checkin_without_comment:method': 1,
                '_authenticator': createToken(),
                },
            )

        for doc in (self.document, self.subdocument):
            manager = getMultiAdapter(
                (doc, self.portal.REQUEST),
                ICheckinCheckoutManager,
                )

            self.assertEquals(None, manager.get_checked_out_by())

            self.assert_journal_entry(
                doc,
                DOCUMENT_CHECKED_IN,
                u'Document checked in',
                comment='',
                )

    @browsing
    def test_multi_checkin_shows_message_when_no_documents_are_selected(self, browser):
        self.login(self.regular_user, browser)

        browser.open(
            self.dossier,
            data={
                'paths': [],
                'checkin_without_comment:method': 1,
                '_authenticator': createToken(),
                },
            )

        self.assertEquals(
            ['You have not selected any documents.'],
            error_messages(),
            )

        redirect_target_url = ''.join((
            self.dossier.absolute_url(),
            '#documents'
            ))

        self.assertEquals(
            redirect_target_url,
            browser.url,
            )

        browser.open(
            self.dossier,
            data={
                'paths': [],
                'checkin_documents:method': 1,
                '_authenticator': createToken(),
                },
            )

        browser.click_on('Checkin')

        self.assertEquals(
            ['You have not selected any documents.'],
            error_messages(),
            )

        self.assertIn(
            redirect_target_url,
            browser.url,
            )

    @browsing
    def test_multi_checkin_does_not_checkin_locked_documents(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')
        browser.find('Checkout and edit').click()

        browser.open(self.subdocument, view='tabbedview_view-overview')
        browser.find('Checkout and edit').click()

        lockable = IRefreshableLockable(self.document)
        lockable.lock()

        browser.open(
            self.dossier,
            method='POST',
            data={
                'paths': [
                    obj2brain(self.document).getPath(),
                    obj2brain(self.subdocument).getPath(),
                    ],
                'checkin_without_comment:method': 1,
                '_authenticator': createToken(),
                },
            )

        manager = getMultiAdapter((self.document, self.portal.REQUEST), ICheckinCheckoutManager)
        self.assertEquals('kathi.barfuss', manager.get_checked_out_by())

        manager = getMultiAdapter((self.subdocument, self.portal.REQUEST), ICheckinCheckoutManager)
        self.assertEquals(None, manager.get_checked_out_by())

        self.assertEquals([u'Could not check in document Vertr\xe4gsentwurf'],
                          error_messages())


# TODO: rewrite this test-case to express intent
class TestCheckinCheckoutManagerAPI(FunctionalTestCase):
    """Tests for the complete checkin-checkout cycle."""

    def setUp(self):
        super(TestCheckinCheckoutManagerAPI, self).setUp()

        self.repo, self.repo_folder = create(Builder('repository_tree'))

        self.dossier = create(Builder('dossier').within(self.repo_folder))
        self.doc1 = create(
            Builder('document')
            .within(self.dossier)
            .titled(u'Document1')
            .with_dummy_content())
        self.doc2 = create(
            Builder('document')
            .within(self.dossier)
            .titled(u'Document2')
            .with_dummy_content())

    def test_api(self):
        # create a defaultfolder
        pr = getToolByName(self.portal, 'portal_repository')

        # create a document, and get CheckinCheckoutManager for the document
        manager = getMultiAdapter(
            (self.doc1, self.portal.REQUEST), ICheckinCheckoutManager)
        manager2 = getMultiAdapter(
            (self.doc2, self.portal.REQUEST), ICheckinCheckoutManager)

        # Checkout:
        # checkout should now allowed, but just for a user with authorization
        self.assertTrue(manager.is_checkout_allowed())

        # the annotations should be still empty
        self.assertIsNone(manager.get_checked_out_by())

        # checkout the document
        manager.checkout()
        self.assertEquals('test_user_1_', manager.get_checked_out_by())

        # cancelling and checkin should be allowed for the 'test_user_1_'
        self.assertTrue(manager.is_checkin_allowed())
        self.assertTrue(manager.is_cancel_allowed())

        self.assertFalse(manager.is_checkout_allowed())

        # Checkout when locked by another user:

        # Create a second user to test locking and checkout
        self.portal.acl_users.userFolderAddUser(
            'other_user', 'secret', ['Member'], [])

        # Checkout should first be allowed
        self.assertTrue(manager2.is_checkout_allowed())

        # Switch to different user and lock the document
        logout()
        login(self.portal, 'other_user')
        setRoles(
            self.portal, 'other_user', ['Manager', 'Editor', 'Contributor'])
        lockable = IRefreshableLockable(self.doc2)
        lockable.lock()

        # Log back in as the regular test user
        logout()
        login(self.portal, TEST_USER_NAME)
        setRoles(
            self.portal, TEST_USER_ID, ['Manager', 'Editor', 'Contributor'])

        # Checkout should not be allowed since the document is already
        # locked by an another user
        self.assertFalse(manager2.is_checkout_allowed())

        # checkin and cancelling:
        mok_file2 = NamedBlobFile('blubb blubb', filename=u"blubb.txt")
        self.doc1.file = mok_file2
        manager.checkin(comment="Test commit Nr. 1")

        transaction.commit()

        # document isn't checked out and the old object is in the history
        self.assertIsNone(manager.get_checked_out_by())

        self.assertEquals(u'Document1.doc',
                          pr.retrieve(self.doc1, 0).object.file.filename)
        self.assertEquals(u'blubb.txt', self.doc1.file.filename)

        manager.checkout()
        self.assertEquals('test_user_1_', manager.get_checked_out_by())

        manager.cancel()
        pr.getHistoryMetadata(self.doc1).retrieve(2)

        self.assertIsNone(manager.get_checked_out_by())
