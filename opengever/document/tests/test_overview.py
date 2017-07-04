from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.core.testing import OPENGEVER_FUNCTIONAL_MEETING_LAYER
from opengever.document.checkout.manager import CHECKIN_CHECKOUT_ANNOTATIONS_KEY  # noqa
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.locking.interfaces import IRefreshableLockable
from zope.annotation.interfaces import IAnnotations
from zope.component import queryMultiAdapter
import transaction


class TestDocumentOverview(FunctionalTestCase):
    """Test the document overview."""

    def setUp(self):
        super(TestDocumentOverview, self).setUp()
        self.repo, self.repo_folder = create(Builder('repository_tree'))

        self.dossier = create(Builder('dossier').within(self.repo_folder))
        self.document = create(
            Builder('document').within(self.dossier).with_dummy_content())

        transaction.commit()

    def tearDown(self):
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        super(TestDocumentOverview, self).tearDown()

    @browsing
    def test_overview_displays_related_documents(self, browser):
        self.doc_a = create(Builder('document')
                            .having(title=u'A\xf6'))
        self.doc_b = create(Builder('document')
                            .having(title=u'B\xf6')
                            .relate_to(self.doc_a))
        self.doc_c = create(Builder('document')
                            .having(title=u'C\xf6')
                            .relate_to(self.doc_b))

        browser.login().open(self.doc_b, view='tabbedview_view-overview')

        self.assertEquals(
            [self.doc_a.title, self.doc_c.title],
            browser.css('ul.related_documents a').text
        )

    @browsing
    def test_overview_has_edit_link(self, browser):
        browser.login().open(self.document, view='tabbedview_view-overview')
        self.assertEquals('Checkout and edit',
                          browser.css('a.function-edit').first.text)
        self.assertEquals(
            '{0}/editing_document'.format(
                self.document.absolute_url()),
            browser.css('a.function-edit').first.attrib['href'].split('?', 1)[0])

    @browsing
    def test_overview_has_creator_link(self, browser):
        browser.login().open(self.document, view='tabbedview_view-overview')
        self.assertEquals('Test User (test_user_1_)',
                          browser.css('td [href*="user-details"]').first.text)
        self.assertEquals(
            '{0}/@@user-details/test_user_1_'.format(
                self.portal.absolute_url()),
            browser.css('td [href*="user-details"]').first.attrib['href'])

    @browsing
    def test_overview_has_copy_link(self, browser):
        browser.login().open(self.document, view='tabbedview_view-overview')
        self.assertEquals('Download copy',
                          browser.css('a.function-download-copy').first.text)

        url = browser.css('a.function-download-copy').first.attrib['href']
        self.assertTrue(url.startswith(
            '{0}/file_download_confirmation'.format(
                self.document.absolute_url())),
            'unexpected url {}'.format(url))

    @browsing
    def test_overview_self_checked_out(self, browser):
        """Check the document overview when the document is checked out,
        by your self (TEST_USER_ID):
        - checked out by information
        - edit link is still available
        """
        manager = queryMultiAdapter(
            (self.document, self.portal.REQUEST), ICheckinCheckoutManager)
        manager.checkout()

        browser.login().visit(self.document, view='tabbedview_view-overview')

        self.assertEquals('Test User (test_user_1_)',
                          browser.css('[href*="user-details"]').first.text)

        self.assertEquals('Checkout and edit',
                          browser.css('a.function-edit').first.text)

        self.assertEquals('Download copy',
                          browser.css('a.function-download-copy').first.text)

    @browsing
    def test_checkout_and_edit(self, browser):
        manager = queryMultiAdapter(
            (self.document, self.portal.REQUEST), ICheckinCheckoutManager)

        self.assertEquals(
            None, manager.get_checked_out_by(),
            'Didn\'t expect the document to be checked out yet.')

        browser.login().open(self.document, view='tabbedview_view-overview')
        browser.find('Checkout and edit').click()

        self.assertEquals(self.document.absolute_url(), browser.url,
                          'editing_document should redirect back to document')

        self.assertEquals(
            TEST_USER_ID, manager.get_checked_out_by(),
            'The document should be checked out by the test user now.')

        self.assertIn(
            self.document.absolute_url() + '/external_edit',
            browser.css('script.redirector').first.text,
            'Redirector should open external_edit.')

    @browsing
    def test_inactive_links_if_document_is_checked_out(self, browser):
        """Check the document overview when the document is checked out,
        by another user:
        - checked out information
        - edit link is inactive
        """
        IAnnotations(self.document)[
            CHECKIN_CHECKOUT_ANNOTATIONS_KEY] = 'hugo.boss'

        transaction.commit()

        browser.login().visit(self.document, view='tabbedview_view-overview')

        self.assertEquals('Checkout and edit',
                          browser.css('.function-edit-inactive').first.text)
        self.assertEquals(
            'Download copy',
            browser.css('.function-download-copy-inactive').first.text)

    @browsing
    def test_checkout_not_possible_if_locked_by_another_user(self, browser):
        second_user = create(Builder('user').with_roles('Member'))

        login(self.portal, second_user.getId())
        lockable = IRefreshableLockable(self.document)
        lockable.lock()

        logout()
        login(self.portal, TEST_USER_NAME)
        transaction.commit()

        browser.login().visit(self.document, view='tabbedview_view-overview')
        self.assertFalse(browser.css('a.function-edit'),
                         'There should be no edit link')

    @browsing
    def test_classification_fields_are_shown(self, browser):
        browser.login().visit(self.document, view='tabbedview_view-overview')

        self.assertEquals(
            'unprotected',
            browser.css(
                '#form-widgets-IClassification-classification').first.text)

        self.assertEquals(
            'privacy_layer_no',
            browser.css(
                '#form-widgets-IClassification-privacy_layer').first.text)

        self.assertEquals(
            'unchecked',
            browser.css(
                '#form-widgets-IClassification-public_trial').first.text)

        self.assertEquals(
            '',
            browser.css(
                '#form-widgets-IClassification-public_trial_statement')
            .first.text)

    @browsing
    def test_modify_public_trial_link_NOT_shown_on_open_dossier(self, browser):
        dossier = create(Builder('dossier').within(self.repo_folder))
        document = create(Builder('document')
                          .within(dossier)
                          .with_dummy_content())
        browser.login().visit(document, view='tabbedview_view-overview')

        self.assertFalse(
            browser.css(
                '#form-widgets-IClassification-public_trial-edit-link'),
            'Public trial edit link should not be visible.')

    @browsing
    def test_modify_public_trial_is_visible_on_closed_dossier(self, browser):
        dossier = create(Builder('dossier')
                         .within(self.repo_folder)
                         .in_state('dossier-state-resolved'))

        document = create(Builder('document')
                          .within(dossier)
                          .with_dummy_content())
        browser.login().visit(document, view='tabbedview_view-overview')

        self.assertTrue(
            browser.css(
                '#form-widgets-IClassification-public_trial-edit-link'),
            'Public trial edit link should be visible.')

    @browsing
    def test_modify_public_trial_is_visible_on_closed_dossier_inside_a_task(self, browser):  # noqa
        dossier = create(Builder('dossier')
                         .within(self.repo_folder)
                         .in_state('dossier-state-resolved'))
        task = create(Builder('task')
                      .within(dossier)
                      .in_state('task-state-tested-and-closed'))
        document = create(Builder('document')
                          .within(task)
                          .with_dummy_content())

        browser.login().visit(document, view='tabbedview_view-overview')

        self.assertTrue(browser.css(
            '#form-widgets-IClassification-public_trial-edit-link'),
                        'Public trial edit link should be visible.')

    @browsing
    def test_submitted_documents_hidden_when_feature_disabled(self, browser):
        container = create(Builder('committee_container'))
        self.committee = create(Builder('committee').within(container))
        self.proposal = create(Builder('proposal')
                               .within(self.dossier)
                               .having(title=u'Pr\xf6posal',
                                       committee=self.committee.load_model())
                               .relate_to(self.document)
                               .as_submitted())

        browser.login().open(self.document, view='tabbedview_view-overview')
        proposals = browser.css('#proposals_box .proposal')
        self.assertEqual(0, len(proposals))

    @browsing
    def test_archival_file_is_only_available_for_managers_by_default(self, browser):  # noqa
        doc = create(Builder('document')
                     .attach_archival_file_containing('TEST', name=u'test.pdf')
                     .with_dummy_content())
        browser.login().visit(doc, view='tabbedview_view-overview')

        self.assertNotIn('Archival File', browser.css('.listing th').text)

    @browsing
    def test_edit_archival_file_link_NOT_shown_on_open_dossier(self, browser):
        self.grant('Manager')
        dossier = create(Builder('dossier').within(self.repo_folder))
        document = create(Builder('document')
                          .within(dossier)
                          .with_dummy_content())
        browser.login().visit(document, view='tabbedview_view-overview')

        self.assertFalse(browser.css('#archival_file_edit_link'),
                         'Archival file edit link should not be visible.')

    @browsing
    def test_edit_archival_file_link_is_visible_on_closed_dossier(self, browser):  # noqa
        self.grant('Manager')
        dossier = create(
            Builder('dossier')
            .within(self.repo_folder)
            .in_state('dossier-state-resolved'))

        document = create(Builder('document')
                          .within(dossier)
                          .with_dummy_content())
        browser.login().visit(document, view='tabbedview_view-overview')

        self.assertEquals(
            '{}/edit_archival_file'.format(document.absolute_url()),
            browser.css('#archival_file_edit_link').first.get('href'))

    @browsing
    def test_edit_archival_file_link_is_visible_on_closed_dossier_inside_a_task(self, browser):  # noqa
        self.grant('Manager')
        dossier = create(Builder('dossier')
                         .within(self.repo_folder)
                         .in_state('dossier-state-resolved'))
        task = create(Builder('task')
                      .within(dossier)
                      .in_state('task-state-tested-and-closed'))
        document = create(Builder('document')
                          .within(task)
                          .with_dummy_content())

        browser.login().visit(document, view='tabbedview_view-overview')

        self.assertEquals(
            '{}/edit_archival_file'.format(document.absolute_url()),
            browser.css('#archival_file_edit_link').first.get('href'))

    @browsing
    def test_archival_file_is_extended_with_mimetype_class(self, browser):
        self.grant('Manager')
        doc = create(Builder('document')
                     .attach_archival_file_containing(
                         'TEST', name=u'test.pdf')
                     .with_dummy_content())
        browser.login().visit(doc, view='tabbedview_view-overview')

        archival_file_row = browser.css('.listing tr')[-1]
        self.assertEquals('Archival File',
                          archival_file_row.css('th').first.text)
        self.assertEquals('icon-pdf',
                          archival_file_row.css('td span')[0].get('class'))
        self.assertEquals(u'test.pdf \u2014 1 KB',
                          archival_file_row.css('td span')[1].text)


class TestOverviewMeetingFeatures(FunctionalTestCase):
    """Test the document overview also works in a meeting context."""

    layer = OPENGEVER_FUNCTIONAL_MEETING_LAYER

    def setUp(self):
        super(TestOverviewMeetingFeatures, self).setUp()
        self.repo_root, self.repo_folder = create(Builder('repository_tree'))

        self.dossier = create(
            Builder('dossier').within(self.repo_folder))
        self.document = create(Builder('document').within(self.dossier))

        container = create(Builder('committee_container'))
        self.committee = create(Builder('committee').within(container))
        self.proposal = create(Builder('proposal')
                               .within(self.dossier)
                               .having(title=u'Pr\xf6posal',
                                       committee=self.committee.load_model())
                               .relate_to(self.document)
                               .as_submitted())

    @browsing
    def test_submitted_proposal_is_shown_on_document_overview(self, browser):
        browser.login().open(self.document, view='tabbedview_view-overview')

        proposals = browser.css('#proposals_box .proposal')
        self.assertEqual(1, len(proposals))

        proposal = proposals.first
        self.assertEqual(u'Pr\xf6posal', proposal.text)
        self.assertEqual(self.proposal.load_model().get_url(),
                         proposal.css('a').first.get('href'))

    @browsing
    def test_submitted_proposal_link_is_not_shown_for_submitted_documents(self, browser):  # noqa
        committee = create(Builder('committee'))
        proposal = create(Builder('proposal')
                          .within(self.dossier)
                          .having(title='Mach doch',
                                  committee=committee.load_model())
                          .relate_to(self.document)
                          .as_submitted())
        submitted_document = proposal.load_model().submitted_documents[0].resolve_submitted()  # noqa

        browser.login()
        browser.open(submitted_document, view='tabbedview_view-overview')
        proposals = browser.css('#proposals_box .proposal')
        self.assertEqual(0, len(proposals))

    @browsing
    def test_outdated_document_can_be_updated(self, browser):
        # create a new document version
        repository = api.portal.get_tool('portal_repository')
        repository.save(self.document)
        transaction.commit()

        browser.login().open(self.document, view='tabbedview_view-overview')
        browser.find('Update document in proposal').click()
        browser.find('Submit Attachments').click()

        self.assertEqual(
            [u'A new submitted version of document'
             u' Testdokum\xe4nt has been created.'],
            info_messages())
        self.assertSubmittedDocumentCreated(
            self.proposal, self.document, submitted_version=1)
