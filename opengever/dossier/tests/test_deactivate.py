from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from opengever.testing import FunctionalTestCase
from plone import api
from plone.protect import createToken


class TestDossierDeactivation(FunctionalTestCase):

    def setUp(self):
        super(TestDossierDeactivation, self).setUp()
        self.dossier = create(Builder('dossier'))

    @browsing
    def test_fails_with_resolved_subdossier(self, browser):
        create(Builder('dossier')
               .within(self.dossier)
               .titled(u'b\xe4\xe4\xe4h')
               .in_state('dossier-state-resolved'))

        browser.login().open(self.dossier, view='transition-deactivate',
                             data={'_authenticator': createToken()})
        self.assertEqual(
            u"The Dossier can't be deactivated, the subdossier b\xe4\xe4\xe4h is already resolved",
            error_messages()[0])

    @browsing
    def test_fails_with_checked_out_documents(self, browser):
        create(Builder('document')
               .within(self.dossier)
               .checked_out())

        browser.login().open(self.dossier, view='transition-deactivate',
                             data={'_authenticator': createToken()})
        self.assertEqual(
            u"The Dossier can't be deactivated, not all containeddocuments "
            "are checked in.",
            error_messages()[0])

    @browsing
    def test_not_possible_with_not_closed_tasks(self, browser):
        create(Builder('task')
               .within(self.dossier)
               .in_state('task-state-in-progress'))

        browser.login().open(self.dossier,
                             view='transition-deactivate',
                             data={'_authenticator': createToken()})

        self.assertEqual('dossier-state-active',
                         api.content.get_state(self.dossier))

        self.assertEqual(
            u"The Dossier can't be deactivated, not all contained "
            "tasks are in a closed state.",
            error_messages()[0])

    @browsing
    def test_not_possible_with_active_proposals(self, browser):
        repo = create(Builder('repository'))
        dossier = create(Builder('dossier').within(repo))
        create(Builder('proposal').within(dossier))

        browser.login().open(dossier,
                             view='transition-deactivate',
                             data={'_authenticator': createToken()})

        self.assertEqual('dossier-state-active',
                         api.content.get_state(dossier))
        self.assertEqual(
            u"The Dossier can't be deactivated, it contains active proposals.",
            error_messages()[0])

    @browsing
    def test_recursively_deactivate_subdossier(self, browser):
        subdossier = create(Builder('dossier').within(self.dossier))
        subsubdossier = create(Builder('dossier').within(subdossier))
        create(Builder('task')
               .within(self.dossier)
               .in_state('task-state-tested-and-closed'))

        browser.login().open(self.dossier, view='transition-deactivate',
                             data={'_authenticator': createToken()})

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

        browser.login().open(self.dossier, view='transition-deactivate',
                             data={'_authenticator': createToken()})

        self.assertEqual('dossier-state-inactive',
                         api.content.get_state(self.dossier))
        self.assertEqual('dossier-state-inactive',
                         api.content.get_state(subdossier1))
        self.assertEqual('dossier-state-inactive',
                         api.content.get_state(subdossier2))
