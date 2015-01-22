from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_ID


class TestDossierDeactivation(FunctionalTestCase):

    def setUp(self):
        super(TestDossierDeactivation, self).setUp()
        self.grant('Editor')
        self.dossier = create(Builder('dossier'))

    @browsing
    def test_fails_with_resolved_subdossier(self, browser):
        create(Builder('dossier')
               .within(self.dossier)
               .titled(u'b\xe4\xe4\xe4h')
               .in_state('dossier-state-resolved'))

        browser.login().open(self.dossier, view='transition-deactivate')
        self.assertEqual(
            u"The Dossier can't be deactivated, the subdossier b\xe4\xe4\xe4h is already resolved",
            error_messages()[0])

    @browsing
    def test_fails_with_checked_out_documents(self, browser):
        create(Builder('document')
               .within(self.dossier)
               .checked_out_by(TEST_USER_ID))

        browser.login().open(self.dossier, view='transition-deactivate')
        self.assertEqual(
            u"The Dossier can't be deactivated, not all containeddocuments "
            "are checked in.",
            error_messages()[0])

    @browsing
    def test_recursively_deactivate_subdossier(self, browser):
        subdossier = create(Builder('dossier').within(self.dossier))
        subsubdossier = create(Builder('dossier').within(subdossier))
        browser.login().open(self.dossier, view='transition-deactivate')

        self.assertEqual('dossier-state-inactive',
                         api.content.get_state(self.dossier))
        self.assertEqual('dossier-state-inactive',
                         api.content.get_state(subdossier))
        self.assertEqual('dossier-state-inactive',
                         api.content.get_state(subsubdossier))

    @browsing
    def test_already_inactive_subdossier_will_be_ignored(self, browser):
        subdossier1 = create(Builder('dossier').within(self.dossier))
        subdossier2 = create(Builder('dossier')
                             .within(self.dossier)
                             .in_state('dossier-state-inactive'))

        browser.login().open(self.dossier, view='transition-deactivate')

        self.assertEqual('dossier-state-inactive',
                         api.content.get_state(self.dossier))
        self.assertEqual('dossier-state-inactive',
                         api.content.get_state(subdossier1))
        self.assertEqual('dossier-state-inactive',
                         api.content.get_state(subdossier2))
