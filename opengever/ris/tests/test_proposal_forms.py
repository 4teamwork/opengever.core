from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from opengever.testing import IntegrationTestCase
from zExceptions import Unauthorized


class TestRisProposalViewsDisabled(IntegrationTestCase):

    features = ('!ris',)

    def setUp(self):
        super(TestRisProposalViewsDisabled, self).setUp()
        with self.login(self.manager):
            self.ris_proposal = create(
                Builder('ris_proposal')
                .within(self.dossier)
                .having(document=self.document)
            )

    @browsing
    def test_add_form_is_disabled(self, browser):
        self.login(self.regular_user, browser)
        # This causes an infinite redirection loop between ++add++ and
        # require_login. By enabling exception_bubbling we can catch the
        # Unauthorized exception and end the infinite loop.
        browser.exception_bubbling = True
        with self.assertRaises(Unauthorized):
            # with browser.expect_unauthorized():
            browser.open(self.dossier,
                         view='++add++opengever.ris.proposal')

    @browsing
    def test_edit_form_is_disabled(self, browser):
        self.login(self.regular_user, browser)
        # This causes an infinite redirection loop between edit and
        # require_login. By enabling exception_bubbling we can catch the
        # Unauthorized exception and end the infinite loop.
        browser.exception_bubbling = True
        with self.assertRaises(Unauthorized):
            browser.visit(self.ris_proposal, view='edit')


class TestRisProposalViews(IntegrationTestCase):

    features = ('ris',)

    @browsing
    def test_proposal_can_be_created_in_browser_by_manager(self, browser):
        self.login(self.manager, browser)
        browser.open(self.dossier)
        factoriesmenu.add('Proposal (Manager: Debug)')
        browser.fill({
            'Title': u'A pr\xf6posal',
            'Committee title ': u'Rechnungspr\xfcfungskommission',
            'Committee URL': u'https://example.com/rech/',
            'Proposal Document': u'/'.join(self.document.getPhysicalPath()),
        })
        form = browser.find_form_by_field('Issuer')
        form.find_widget('Issuer').fill(self.dossier_responsible.id)
        form.save()

        statusmessages.assert_no_error_messages()
        statusmessages.assert_message('Item created')
        self.assert_workflow_state('proposal-state-active', browser.context)

    @browsing
    def test_proposal_can_be_edited_in_browser(self, browser):
        self.login(self.dossier_responsible, browser)

        ris_proposal = create(
            Builder('ris_proposal')
            .within(self.dossier)
            .having(document=self.document)
        )

        browser.visit(ris_proposal)
        editbar.contentview('Edit').click()
        self.assertEqual(u'Neue Klarinette', browser.find('Title').value)

        browser.fill({
            'Title': u'Neue Posaune',
            'Description': u'Klarinette quietscht zu fest',
            'Attachments': [self.mail_eml],
        }).save()
        statusmessages.assert_no_error_messages()
        statusmessages.assert_message('Changes saved')

        self.assertEqual(1, len(ris_proposal.attachments))
        self.assertEqual(self.mail_eml, ris_proposal.attachments[0].to_object)
        self.assertEqual(u'Neue Posaune', ris_proposal.title)
        self.assertEqual(
            u'Klarinette quietscht zu fest', ris_proposal.description)
