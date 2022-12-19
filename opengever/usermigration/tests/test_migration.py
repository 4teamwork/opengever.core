# from ftw.usermigration.tests.test_migration_form import make_mapping
# from opengever.document.interfaces import ICheckinCheckoutManager
# from opengever.dossier.behaviors.dossier import IDossier
# from opengever.testing import obj2brain
# from zope.component import getMultiAdapter
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


PRE_MIGRATION_HOOKS = [
    'GEVER: Checked out documents (checked_out_by and WebDAV locks)',
    'GEVER: Creators (obj.creators for all objects)',
    'GEVER: Dictstorage (SQL)',
    'GEVER: Dossiers (responsibles and participations)',
    'GEVER: OGDS Groups (users and inbox groups on OrgUnits)',
    'GEVER: OGDS User References (activities, tasks)',
    'GEVER: Plone Tasks (issuers, responsibles, responses)',
    'GEVER: Private Folders',
    'GEVER: Proposals and submitted proposals',
    'GEVER: Recently touched objects',
    'GEVER: Tasks templates (issuers, responsibles)',
]


class TestUserMigrationForm(IntegrationTestCase):

    maxDiff = None

    def setUp(self):
        super(TestUserMigrationForm, self).setUp()

        self.new_user = create(Builder('user')
            .named('Hans', 'Muster')
            .with_roles(['Member'])
        )
        self.new_ogds_user = create(Builder('ogds_user')
            .id(self.new_user.getId())
            .having(active=True)
        )

    @browsing
    def test_lists_all_pre_migration_hooks(self, browser):
        self.login(self.manager, browser=browser)
        browser.visit(view='user-migration')
        self.assertItemsEqual(
            PRE_MIGRATION_HOOKS,
            browser.css('#form-widgets-pre_migration_hooks .option').text,
        )

    # @browsing
    # def test_runs_pre_migrations_via_browser(self, browser):
    #     self.login(self.dossier_responsible)
    #     ci_co_manager = getMultiAdapter((self.document, self.request),
    #                               ICheckinCheckoutManager)
    #     ci_co_manager.checkout()

    #     self.login(self.manager, browser=browser)
    #     browser.visit(view='user-migration')

    #     mapping = make_mapping(
    #         {
    #             self.dossier_responsible.getId(): self.new_user.getId(),
    #         }
    #     )
    #     browser.fill(
    #         {'Manual Principal Mapping': mapping,
    #          'Migrations': ['globalroles', 'localroles'],
    #          'Pre-Migration Hooks': PRE_MIGRATION_HOOKS}
    #     ).submit()

    #     self.assertEqual('hans.muster', ci_co_manager.get_checked_out_by())
    #     self.assertEqual('hans.muster', obj2brain(self.document).checked_out)

    #     self.assertIn('hans.muster', self.document.creators)
    #     self.assertIn('hans.muster', self.dossier.creators)

    #     self.assertEqual('hans.muster', self.proposal.issuer)
    #     self.assertEqual('hans.muster', self.proposal.load_model().issuer)
    #     self.assertEqual('hans.muster', self.submitted_proposal.issuer)
    #     self.assertEqual('hans.muster', self.submitted_proposal.load_model().issuer)

    #     self.assertEqual('hans.muster', self.task.issuer)
    #     self.assertEqual('hans.muster', self.task.get_sql_object().issuer)
    #     self.assertEqual('hans.muster', self.meeting_task.issuer)
    #     self.assertEqual('hans.muster', self.meeting_task.get_sql_object().issuer)
    #     self.assertEqual('hans.muster', self.inbox_task.issuer)
    #     self.assertEqual('hans.muster', self.inbox_task.get_sql_object().issuer)

    #     self.assertEqual('hans.muster', self.inbox_forwarding.issuer)
    #     self.assertEqual('hans.muster', self.inbox_forwarding.get_sql_object().issuer)

    #     self.assertEqual('hans.muster', IDossier(self.dossier).responsible)
    #     self.assertEqual('hans.muster', IDossier(self.expired_dossier).responsible)
    #     self.assertEqual('hans.muster', IDossier(self.inactive_dossier).responsible)
    #     self.assertEqual('hans.muster', IDossier(self.offered_dossier_to_archive).responsible)
    #     self.assertEqual('hans.muster', IDossier(self.offered_dossier_for_sip).responsible)
    #     self.assertEqual('hans.muster', IDossier(self.offered_dossier_to_destroy).responsible)
    #     self.assertEqual('hans.muster', IDossier(self.protected_dossier).responsible)
