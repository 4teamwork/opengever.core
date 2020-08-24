from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import create_document_version
from opengever.wopi import discovery
from opengever.wopi.interfaces import IWOPISettings
from opengever.wopi.lock import create_lock as create_wopi_lock
from plone import api
from plone.locking.interfaces import IRefreshableLockable
from plone.namedfile.file import NamedBlobFile
from plone.protect import createToken
from plone.registry.interfaces import IRegistry
from urllib import urlencode
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
import time


class TestGetOpenAsPdfURL(IntegrationTestCase):
    """Test the integrity of generated bumblebee links."""

    features = (
        'bumblebee',
        )

    def test_returns_pdf_url_as_string(self):
        self.login(self.regular_user)
        view = api.content.get_view('tabbedview_view-overview',
                                    self.document, self.request)
        self.assertEqual(
            '{}/bumblebee-open-pdf?filename=Vertraegsentwurf.pdf'.format(
                self.document.absolute_url()),
            view.get_open_as_pdf_url())

    def test_returns_none_if_no_mimetype_is_available(self):
        self.login(self.regular_user)
        self.document.file.contentType = u'foo/bar'
        view = api.content.get_view('tabbedview_view-overview',
                                    self.document, self.request)
        self.assertIsNone(view.get_open_as_pdf_url())

    def test_returns_none_if_mimetype_is_not_supported(self):
        self.login(self.regular_user)
        self.document.file = NamedBlobFile(
            data=u'T\xc3\xa4stfil\xc3\xa9',
            contentType='test/notsupported',
            filename=u'test.notsupported')
        view = api.content.get_view('tabbedview_view-overview',
                                    self.document, self.request)
        self.assertIsNone(view.get_open_as_pdf_url())


class TestGetPdfFilename(IntegrationTestCase):
    """Test we generate bumblebee filenames correctly."""

    features = (
        'bumblebee',
        )

    def test_changes_filename_extension_to_pdf_and_returns_filename(self):
        self.login(self.regular_user)
        view = api.content.get_view('tabbedview_view-overview',
                                    self.document, self.request)
        self.document.file.filename = u'Vertr\xe4ge Wichtig.docx'
        self.assertEqual(u'Vertr\xe4ge Wichtig.pdf', view._get_pdf_filename())

    def test_appends_pdf_if_missing_extension(self):
        self.login(self.regular_user)
        view = api.content.get_view('tabbedview_view-overview',
                                    self.document, self.request)
        self.document.file.filename = u'Vertr\xe4ge Wichtig'
        self.assertEqual(u'Vertr\xe4ge Wichtig.pdf', view._get_pdf_filename())


class TestGetCheckoutURL(IntegrationTestCase):
    """Test we correctly generate the document checkout urls."""

    features = (
        'bumblebee',
        )

    def test_get_oc_zem_checkout_url(self):
        self.login(self.regular_user)
        view = api.content.get_view('tabbedview_view-overview',
                                    self.document, self.request)
        expected_url = '{}/editing_document?_authenticator='.format(
            self.document.absolute_url())
        self.assertTrue(view.get_oc_zem_checkout_url().startswith(expected_url))

    def test_get_checkout_url(self):
        self.login(self.regular_user)
        view = api.content.get_view('tabbedview_view-overview',
                                    self.document, self.request)
        expected_url = '{}/@@checkout_documents?_authenticator='.format(
            self.document.absolute_url())
        self.assertTrue(view.get_checkout_url().startswith(expected_url))

    def test_get_oc_direct_checkout_url(self):
        self.login(self.regular_user)
        view = api.content.get_view('tabbedview_view-overview',
                                    self.document, self.request)
        expected_url = (
            u"javascript:officeConnectorCheckout("
            "'{}/officeconnector_checkout_url'"
            ");".format(self.document.absolute_url()))
        self.assertEqual(expected_url, view.get_oc_direct_checkout_url())


class TestGetEditMetadataURL(IntegrationTestCase):
    """Test we correctly generate the document edit metadata link."""

    features = (
        'bumblebee',
        )

    def test_returns_edit_metadata_url(self):
        self.login(self.regular_user)
        view = api.content.get_view('tabbedview_view-overview',
                                    self.document, self.request)
        self.assertEqual(
            '{}/edit_checker'.format(self.document.absolute_url()),
            view.get_edit_metadata_url())


class TestGetCheckinWithoutCommentURL(IntegrationTestCase):
    """Test we correctly generate a checkin without comment link."""

    features = (
        'bumblebee',
        )

    def test_returns_none_when_document_is_not_checked_out(self):
        self.login(self.regular_user)
        view = api.content.get_view('tabbedview_view-overview',
                                    self.document, self.request)
        self.assertIsNone(view.get_checkin_without_comment_url())

    def test_returns_checkin_without_comment_url_as_string(self):
        self.login(self.regular_user)
        self.checkout_document(self.document)
        view = api.content.get_view('tabbedview_view-overview',
                                    self.document, self.request)
        expected_url = '{}/@@checkin_without_comment?_authenticator='.format(
            self.document.absolute_url())
        self.assertTrue(
            view.get_checkin_without_comment_url().startswith(expected_url))


class TestGetCheckinWithCommentURL(IntegrationTestCase):
    """Test we correctly generate a checkin with comment link."""

    features = (
        'bumblebee',
        )

    def test_returns_none_when_document_is_not_checked_out(self):
        self.login(self.regular_user)
        view = api.content.get_view('tabbedview_view-overview',
                                    self.document, self.request)
        self.assertIsNone(view.get_checkin_with_comment_url())

    def test_returns_checkin_with_comment_url_as_string(self):
        self.login(self.regular_user)
        self.checkout_document(self.document)
        view = api.content.get_view('tabbedview_view-overview',
                                    self.document, self.request)
        expected_url = '{}/@@checkin_document?_authenticator='.format(
            self.document.absolute_url())
        self.assertTrue(
            view.get_checkin_with_comment_url().startswith(expected_url))


class TestDocumentOverviewVanilla(IntegrationTestCase):

    features = (
        '!officeconnector-attach',
        '!officeconnector-checkout',
    )

    @staticmethod
    def get_metadata_value(browser, row_head):
        metadata = browser.css('.documentMetadata tr')
        index = [row.cells[0].text for row in metadata].index(row_head)
        return metadata[index].cells[1].text

    @browsing
    def test_overview_displays_creation_date(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, view='tabbedview_view-overview')
        self.assertEqual('Aug 31, 2016 04:07 PM',
                         self.get_metadata_value(browser, "Created"))

    @browsing
    def test_overview_displays_modification_date(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.document, view='tabbedview_view-overview')
        self.assertEqual('Aug 31, 2016 04:07 PM',
                         self.get_metadata_value(browser, "Modified"))

    @browsing
    def test_overview_displays_related_documents_but_only_documents(self, browser):
        self.login(self.regular_user, browser)

        document_chain_link = create(
            Builder('document')
            .within(self.dossier)
            .having(
                title=u'F\xf6\xf6',
                )
            .relate_to(self.document)
            )

        document_chain_end = create(
            Builder('document')
            .within(self.dossier)
            .having(
                title=u'F\xe4\xe4',
                )
            .relate_to(document_chain_link)
            )

        browser.open(document_chain_link, view='tabbedview_view-overview')

        related_documents = browser.css('ul.related_documents a').text

        self.assertEquals(
            2,
            len(related_documents),
            )

        self.assertIn(
            self.document.title,
            related_documents
            )

        self.assertIn(
            document_chain_end.title,
            related_documents
            )

    @browsing
    def test_overview_has_edit_link(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')

        edit_button = browser.css('a.function-edit')

        self.assertEquals(
            1,
            len(edit_button.text),
            )

        self.assertEquals(
            'Checkout and edit',
            edit_button.first.text,
            )

        self.assertIn(
            '/editing_document',
            edit_button.first.attrib['href'],
            )

    @browsing
    def test_overview_has_creator_link(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')

        user_details_link = browser.css('td [href*="user-details"]')

        self.assertEquals(1, len(user_details_link))

        self.assertEquals(
            'Ziegler Robert (robert.ziegler)',
            user_details_link.first.text
            )

        self.assertIn(
            '/@@user-details/robert.ziegler',
            user_details_link.first.attrib['href'],
            )

    @browsing
    def test_keywords_are_listed_on_overview(self, browser):
        self.login(self.regular_user, browser=browser)

        IDocumentSchema(self.document).keywords = u'secret', u'special'

        browser.open(self.document,
                     view='tabbedview_view-overview')

        self.assertEquals([u'secret', u'special'],
                          browser.css('.keywords a').text)

    @browsing
    def test_overview_has_download_copy_link(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')

        download_copy_link = browser.css('a.function-download-copy')

        self.assertEquals(
            1,
            len(download_copy_link),
            )

        self.assertEquals(
            'Download copy',
            download_copy_link.first.text,
            )

        self.assertIn(
            '/file_download_confirmation',
            download_copy_link.first.attrib['href'],
            )

    @browsing
    def test_overview_self_checked_out(self, browser):
        """Check the document overview when the document is checked out,
        by your self (TEST_USER_ID):
        - checked out by information
        - edit link is still available
        """

        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')
        browser.find('Checkout and edit').click()

        # Tabbedview gets in the way of the redirect so we'll have to revisit
        browser.open(self.document, view='tabbedview_view-overview')

        document_metadata = browser.css('.documentMetadata tr').text

        self.assertIn(
            'Author test_user_1_',
            document_metadata,
            )

        self.assertIn(
            'creator Ziegler Robert (robert.ziegler)',
            document_metadata,
            )

        self.assertIn(
            u'Checked out B\xe4rfuss K\xe4thi (kathi.barfuss)',
            document_metadata,
            )

        file_actions = browser.css('.file-action-buttons a').text

        self.assertIn(
            'Edit',
            file_actions,
            )

        self.assertIn(
            'Checkin without comment',
            file_actions,
            )

        self.assertIn(
            'Checkin with comment',
            file_actions,
            )

        self.assertIn(
            'Download copy',
            file_actions,
            )

    @browsing
    def test_checkout_and_edit(self, browser):
        self.login(self.regular_user, browser)

        manager = queryMultiAdapter(
            (self.document, self.portal.REQUEST),
            ICheckinCheckoutManager,
            )

        self.assertEquals(
            None,
            manager.get_checked_out_by(),
            'Didn\'t expect the document to be checked out yet.'
            )

        browser.open(self.document, view='tabbedview_view-overview')
        browser.find('Checkout and edit').click()

        self.assertEquals(
            self.document.absolute_url(),
            browser.url,
            'editing_document should redirect back to document',
            )

        self.assertEquals(
            'kathi.barfuss',
            manager.get_checked_out_by(),
            'The document should be checked out by the test user now.',
            )

        self.assertIn(
            '/'.join((
                self.document.absolute_url(),
                'external_edit'
                )),
            browser.css('script.redirector').first.text,
            'Redirector should open external_edit.',
            )

    @browsing
    def test_inactive_links_if_document_is_checked_out(self, browser):
        """Check the document overview when the document is checked out,
        by another user:
        - checked out information
        - edit link is inactive
        """

        self.login(self.dossier_responsible, browser)

        browser.open(self.document, view='tabbedview_view-overview')
        browser.find('Checkout and edit').click()

        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertFalse(
            browser.css('a.function-edit'),
            'There should be no edit link',
            )

        self.assertEquals(
            'Checkout and edit',
            browser.css('.function-edit-inactive').first.text,
            )

        self.assertFalse(
            browser.css('a.function-download-copy'),
            'There should be no edit link',
            )

        self.assertEquals(
            'Download copy',
            browser.css('.function-download-copy-inactive',).first.text,
            )

    @browsing
    def test_inactive_links_if_unsupported_format(self, browser):
        """Check the document overview when the document's format is not,
        supported by office connector:
        - Edit link is inactive
        - Checkout link is active
        """
        self.login(self.regular_user, browser)
        browser.open(self.document, view='tabbedview_view-overview')
        self.assertFalse(browser.css('.function-edit-inactive'), 'There should not be an inactive edit button')

        self.document.file.contentType = "application/foo"
        browser.open(self.document, view='tabbedview_view-overview')

        edit_button = browser.css('a.function-edit')

        self.assertEquals(
            1,
            len(edit_button.text),
        )

        self.assertEquals(
            'Checkout',
            edit_button.first.text,
        )

        self.assertIn(
            '/@@checkout_documents',
            edit_button.first.attrib['href'],
        )

        self.assertTrue(browser.css('.function-edit-inactive'),
                        'There should be an inactive edit button')

    @browsing
    def test_checkout_not_possible_if_locked_by_another_user(self, browser):
        self.login(self.dossier_responsible, browser)

        lockable = IRefreshableLockable(self.document)
        lockable.lock()

        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')
        self.assertFalse(
            browser.css('a.function-edit'),
            'There should be no edit link',
            )

    @browsing
    def test_classification_fields_are_shown(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEquals(
            'unprotected',
            browser.css(
                '#form-widgets-IClassification-classification',
                ).first.text,
            )

        self.assertEquals(
            'privacy_layer_no',
            browser.css(
                '#form-widgets-IClassification-privacy_layer',
                ).first.text,
            )

        self.assertEquals(
            'unchecked',
            browser.css(
                '#form-widgets-IClassification-public_trial',
                ).first.text,
            )

    @browsing
    def test_modify_public_trial_link_NOT_shown_on_open_dossier(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertFalse(
            browser.css('#form-widgets-IClassification-public_trial_statement')
            .first
            .text,
            'Public trial edit link should not be visible.',
            )

    @browsing
    def test_modify_public_trial_is_visible_on_closed_dossier(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertTrue(
            browser.css('#form-widgets-IClassification-public_trial-edit-link')
            .first
            .text,
            'Public trial edit link should be visible.')

    @browsing
    def test_modify_public_trial_link_NOT_shown_on_inbox_documents(self, browser):
        self.login(self.secretariat_user, browser)

        browser.open(self.inbox_document, view='tabbedview_view-overview')

        self.assertFalse(
            browser.css('#form-widgets-IClassification-public_trial_statement').first.text,
            'Public trial edit link should not be visible.')

    @browsing
    def test_modify_public_trial_is_visible_on_closed_dossier_inside_a_task(self, browser):
        self.login(self.regular_user, browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)

        browser.open(self.taskdocument, view='tabbedview_view-overview')

        self.assertTrue(
            browser.css('#form-widgets-IClassification-public_trial-edit-link')
            .first
            .text,
            'Public trial edit link should be visible.',
            )

    @browsing
    def test_submitted_documents_hidden_when_feature_disabled(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')

        self.assertEqual(0, len(browser.css('#proposals_box .proposal')))

    @browsing
    def test_archival_file_rows_only_visible_for_managers_by_default(self, browser):
        # Both the archival file and archival file state rows are only shown
        # for managers (users with the 'Modify archival file' permission)
        self.login(self.regular_user, browser)

        browser.open(self.expired_document, view='tabbedview_view-overview')

        document_attributes = [
            'Title',
            'Document Date',
            'File',
            'Created',
            'Modified',
            'Document Type',
            'Author',
            'creator',
            'Description',
            'Keywords',
            'Foreign Reference',
            'Checked out',
            'Digital Available',
            'Preserved as paper',
            'Date of receipt',
            'Date of delivery',
            'Related Documents',
            'Classification',
            'Privacy layer',
            'Public Trial',
            'Public trial statement',
            ]

        self.assertEquals(document_attributes, browser.css('.listing th').text)

        self.login(self.manager, browser)
        browser.open(self.expired_document, view='tabbedview_view-overview')

        document_attributes.extend(["Archival File", "Archival file state"])

        self.assertEquals(document_attributes, browser.css('.listing th').text)

    @browsing
    def test_edit_archival_file_link_NOT_shown_on_open_dossier(self, browser):
        self.login(self.manager, browser)
        self.set_workflow_state('dossier-state-active', self.expired_dossier)

        browser.open(self.expired_document, view='tabbedview_view-overview')

        self.assertFalse(
            browser.css('#archival_file_edit_link'),
            'Archival file edit link should not be visible.',
            )

    @browsing
    def test_edit_archival_file_link_is_visible_on_closed_dossier(self, browser):
        self.login(self.manager, browser)

        browser.open(self.expired_document, view='tabbedview_view-overview')

        self.assertIn(
            '/edit_archival_file',
            browser.css('#archival_file_edit_link').first.get('href'),
            )

    @browsing
    def test_edit_archival_file_link_is_disabled_on_inbox_documents(self, browser):
        self.login(self.secretariat_user, browser)

        browser.open(self.inbox_document, view='tabbedview_view-overview')

        self.assertFalse(
            browser.css('#archival_file_edit_link'),
            'Archival file edit link should not be visible.')

    @browsing
    def test_edit_archival_file_link_is_visible_on_closed_dossier_inside_a_task(self, browser):
        self.login(self.manager, browser)
        self.set_workflow_state('dossier-state-resolved', self.dossier)
        self.set_workflow_state('task-state-tested-and-closed', self.task)

        browser.open(self.taskdocument, view='tabbedview_view-overview')

        self.assertIn(
            '/edit_archival_file',
            browser.css('#archival_file_edit_link').first.get('href'),
            )

    @browsing
    def test_archival_file_is_extended_with_mimetype_class(self, browser):
        self.login(self.manager, browser)

        browser.open(self.expired_document, view='tabbedview_view-overview')

        archival_file_row_index = browser.css('.listing tr th').text.index("Archival File")
        archival_file_row = browser.css('.listing tr')[archival_file_row_index]

        self.assertEquals(
            'Archival File',
            archival_file_row.css('th').first.text,
            )

        self.assertEquals(
            'icon-pdf',
            archival_file_row.css('td span')[0].get('class'),
            )

        self.assertEquals(
            u'test.pdf \u2014 1 KB',
            archival_file_row.css('td span')[1].text,
            )

    @browsing
    def test_checkin_without_comment_action_button_not_rendered_for_locked_documents(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')
        browser.find('Checkout and edit').click()

        lockable = IRefreshableLockable(self.document)
        lockable.lock()

        # Tabbedview gets in the way of the redirect so we'll have to revisit
        browser.open(self.document, view='tabbedview_view-overview')

        file_actions = [
            'Edit',
            'Checkin with comment',
            'Download copy',
            ]

        self.assertEquals(
            file_actions,
            browser.css('.file-action-buttons a').text,
            )

    @browsing
    def test_checkin_without_comment_portal_action_not_rendered_for_locked_documents(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')
        browser.find('Checkout and edit').click()

        lockable = IRefreshableLockable(self.document)
        lockable.lock()

        browser.open(self.document)

        document_portal_actions = [
            'Edit metadata',
            u'Actions \u25bc',
            'Properties',
            u'Checkin \u25bc',
            'with comment',
            ]

        self.assertEquals(
            document_portal_actions,
            browser.css('#edit-bar a').text
            )

    @browsing
    def test_description_is_intelligently_formatted(self, browser):
        self.login(self.regular_user, browser)
        self.document.description = u'\n\n Foo\n    Bar\n'
        browser.open(self.document, view='tabbedview_view-overview')
        # Somehow what is `&nbsp;` in a browser is `\xa0` in ftw.testbrowser
        self.assertEqual(
            u'<br><br>\xa0Foo<br>\xa0\xa0\xa0\xa0Bar<br>',
            browser.css('#form-widgets-IDocumentMetadata-description')[0].innerHTML,
        )

    @browsing
    def test_description_does_not_display_none_value(self, browser):
        self.login(self.regular_user, browser)
        self.document.description = None
        browser.open(self.document, view='tabbedview_view-overview')
        self.assertEqual(
            u'',
            browser.css('#form-widgets-IDocumentMetadata-description')[0].innerHTML,
        )

    @browsing
    def test_webactions_are_shown_in_overview(self, browser):
        self.login(self.regular_user, browser)

        create(Builder('webaction')
               .titled(u'\xc4ction 1')
               .having(order=5,
                       display='action-buttons',
                       icon_name="fa-helicopter"))

        create(Builder('webaction')
               .titled(u'Action 2')
               .having(order=1,
                       display='action-buttons',
                       target_url="http://example.org/endpoint2"))

        browser.open(self.document, view='tabbedview_view-overview')

        webactions = browser.css('.file-action-buttons a.webaction_button')
        self.assertEqual(['Action 2', u'\xc4ction 1'], webactions.text)

        params = urlencode({'context': self.document.absolute_url(),
                            'orgunit': 'fa'})
        self.assertEqual(map(lambda item: item.get("href"), webactions),
                         ['http://example.org/endpoint2?{}'.format(params),
                          'http://example.org/endpoint?{}'.format(params)])

        self.assertEqual(
            map(lambda item: item.get("class"), webactions),
            ['webaction_button', 'webaction_button fa fa-helicopter'])

    @browsing
    def test_webactions_are_html_escaped(self, browser):
        self.login(self.regular_user, browser)

        create(Builder('webaction')
               .titled(u'<bold>Action with HTML</bold>')
               .having(display='action-buttons'))

        browser.open(self.document, view='tabbedview_view-overview')

        webactions = browser.css('.file-action-buttons a.webaction_button')
        self.assertIn('&lt;bold&gt;Action with HTML&lt;/bold&gt;', webactions[0].innerHTML)


class TestDocumentOverviewWithMeeting(IntegrationTestCase):

    features = ('meeting', )

    @browsing
    def test_submitted_proposal_is_shown_on_document_overview(self, browser):
        self.login(self.meeting_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')

        proposals = browser.css('#proposals_box .proposal')
        self.assertEqual(1, len(proposals))

        proposal = proposals.first

        self.assertEquals(
            u'Vertr\xe4ge',
            proposal.text,
            )

        self.assertEquals(
            self.proposal.load_model().get_url(),
            proposal.css('a').first.get('href'),
            )

    @browsing
    def test_submitted_proposal_link_is_not_shown_for_submitted_documents(self, browser):
        self.login(self.meeting_user, browser)

        submitted_document = (
            self.proposal.load_model()
            .submitted_documents[0]
            .resolve_submitted()
            )

        browser.open(submitted_document, view='tabbedview_view-overview')

        proposals = browser.css('#proposals_box .proposal')
        self.assertEqual(0, len(proposals))

    @browsing
    def test_outdated_document_can_be_updated(self, browser):
        self.login(self.meeting_user, browser)

        # No initial versions anymore, so have to do two versions
        create_document_version(self.document, 0)
        create_document_version(self.document, 1)

        browser.open(self.document, view='tabbedview_view-overview')

        browser.find('Update document in proposal').click()
        browser.find('Submit Attachments').click()

        self.assertEqual(
            [
                (
                    u'A new submitted version of document'
                    u' Vertr\xe4gsentwurf has been created.'
                    ),
                ],
            info_messages(),
            )

        self.assertSubmittedDocumentCreated(self.proposal, self.document, submitted_version=1)


class TestDocumentOverviewWithOfficeOnline(IntegrationTestCase):

    features = (
        '!officeconnector-attach',
        '!officeconnector-checkout',
    )

    def setUp(self):
        super(TestDocumentOverviewWithOfficeOnline, self).setUp()

        # Enable WOPI / Office Online support
        settings = getUtility(IRegistry).forInterface(IWOPISettings)
        settings.enabled = True
        settings.discovery_url = u'http://localhost/hosting/discovery'

        discovery._WOPI_DISCOVERY = {
            'timestamp': time.time(),
            'url': settings.discovery_url,
            'editable-extensions': set(['docx', 'xlsx', 'pptx']),
        }

    @browsing
    def test_has_additional_office_online_edit_button(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')

        edit_buttons = browser.css('a.function-edit')

        self.assertEquals(['Checkout and edit', 'Edit in Office Online'],
                          [btn.text for btn in edit_buttons])

        self.assertIn('/editing_document', edit_buttons[0].attrib['href'])
        self.assertIn('/office_online_edit', edit_buttons[1].attrib['href'])

    @browsing
    def test_office_online_editable_if_collaboratively_checked_out_by_self(self, browser):
        self.login(self.regular_user, browser)

        manager = getMultiAdapter(
            (self.document, self.request), ICheckinCheckoutManager)

        # Collaboratively check out and acquire WOPI lock
        manager.checkout(collaborative=True)
        create_wopi_lock(self.document, 'my-token')

        # Tabbedview gets in the way of the redirect so we'll have to revisit
        browser.open(self.document, view='tabbedview_view-overview')

        document_metadata = browser.css('.documentMetadata tr').text

        self.assertIn(
            u'Checked out B\xe4rfuss K\xe4thi (kathi.barfuss)',
            document_metadata,
        )

        file_actions = browser.css('.file-action-buttons a').text

        # Collaborative checkout by self:
        # - "Edit in Office Online" action is available
        # But not:
        # - Edit [with OfficeConnector] (because it's a collaborative checkout)
        # - Cancel checkout (because it's locked)
        # - Checkin (because it's a collaborative checkout)
        self.assertEquals(
            ['Edit in Office Online',
             'Download copy'],
            file_actions)

    @browsing
    def test_office_online_editable_if_collaboratively_checked_out_by_other(self, browser):
        self.login(self.dossier_responsible, browser)

        manager = getMultiAdapter(
            (self.document, self.request), ICheckinCheckoutManager)

        # Collaboratively check out and acquire WOPI lock
        manager.checkout(collaborative=True)
        create_wopi_lock(self.document, 'my-token')

        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')

        document_metadata = browser.css('.documentMetadata tr').text

        self.assertIn(
            u'Checked out Ziegler Robert (robert.ziegler)',
            document_metadata,
        )

        file_actions = browser.css('.file-action-buttons a').text

        # Collaborative checkout by someone else:
        # - "Edit in Office Online" action is available
        # But not:
        # - Cancel checkout (because it's locked)
        # - Checkin (because it's a collaborative checkout)
        # - Edit (checked out by someone else)
        # - Download copy (checked out by someone else)
        self.assertEquals(
            ['Edit in Office Online'],
            file_actions)

    @browsing
    def test_not_office_online_editable_if_regularly_checked_out_by_self(self, browser):
        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')
        browser.find('Checkout and edit').click()

        # Tabbedview gets in the way of the redirect so we'll have to revisit
        browser.open(self.document, view='tabbedview_view-overview')

        document_metadata = browser.css('.documentMetadata tr').text

        self.assertIn(
            u'Checked out B\xe4rfuss K\xe4thi (kathi.barfuss)',
            document_metadata,
        )

        file_actions = browser.css('.file-action-buttons a').text

        # "Edit in Office Online" action not shown (regular checkout by self)
        self.assertEquals(
            ['Edit',
             'Checkin without comment',
             'Checkin with comment',
             'Cancel checkout',
             'Download copy'],
            file_actions)

    @browsing
    def test_not_office_online_editable_if_regularly_checked_out_by_other(self, browser):
        self.login(self.dossier_responsible, browser)

        browser.open(self.document, view='tabbedview_view-overview')
        browser.find('Checkout and edit').click()

        self.login(self.regular_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')

        document_metadata = browser.css('.documentMetadata tr').text

        self.assertIn(
            u'Checked out Ziegler Robert (robert.ziegler)',
            document_metadata,
        )

        file_actions = browser.css('.file-action-buttons a').text

        # "Edit in Office Online" action not shown (regular checkout by other)
        self.assertEquals([], file_actions)

    @browsing
    def test_not_office_online_editable_if_in_resolved_dossier(self, browser):
        self.login(self.secretariat_user, browser)

        browser.open(self.resolvable_dossier,
                     view='transition-resolve',
                     data={'_authenticator': createToken()})

        self.login(self.regular_user, browser)

        # Tabbedview gets in the way of the redirect so we'll have to revisit
        browser.open(self.resolvable_document, view='tabbedview_view-overview')

        file_actions = browser.css('.file-action-buttons a').text

        # "Edit in Office Online" action not shown (resolved dossier)
        self.assertEquals(
            ['Download copy'],
            file_actions)

    @browsing
    def test_not_office_online_editable_if_in_inactive_dossier(self, browser):
        self.login(self.secretariat_user, browser)

        browser.open(self.resolvable_dossier,
                     view='transition-deactivate',
                     data={'_authenticator': createToken()})

        self.login(self.regular_user, browser)

        # Tabbedview gets in the way of the redirect so we'll have to revisit
        browser.open(self.resolvable_document, view='tabbedview_view-overview')

        file_actions = browser.css('.file-action-buttons a').text

        # "Edit in Office Online" action not shown (inactive dossier)
        self.assertEquals(
            ['Download copy'],
            file_actions)
