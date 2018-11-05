from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import create_document_version
from plone.locking.interfaces import IRefreshableLockable
from zope.component import queryMultiAdapter


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
    def test_archival_file_is_only_available_for_managers_by_default(self, browser):
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

        archival_file_row = browser.css('.listing tr')[-1]

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
            'Copy Item',
            'Properties',
            u'Checkin \u25bc',
            'with comment',
            ]

        self.assertEquals(
            document_portal_actions,
            browser.css('#edit-bar a').text
            )


class TestDocumentOverviewWithMeeting(IntegrationTestCase):

    features = ('meeting', )

    @browsing
    def test_submitted_proposal_is_shown_on_document_overview(self, browser):
        self.login(self.meeting_user, browser)

        browser.open(self.document, view='tabbedview_view-overview')

        proposals = browser.css('#proposals_box .proposal')
        self.assertEqual(2, len(proposals))

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
