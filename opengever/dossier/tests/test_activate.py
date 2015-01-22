from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.testing import FunctionalTestCase
from plone import api


class TestDossierActivation(FunctionalTestCase):

    def setUp(self):
        super(TestDossierActivation, self).setUp()
        self.grant('Editor', 'Publisher')
        self.dossier = create(Builder('dossier')
                              .in_state('dossier-state-inactive'))

    @browsing
    def test_recursively_activates_subdossier(self, browser):
        subdossier = create(Builder('dossier')
                            .within(self.dossier)
                            .in_state('dossier-state-inactive'))
        subsubdossier = create(Builder('dossier')
                               .within(subdossier)
                               .in_state('dossier-state-inactive'))

        browser.login().open(self.dossier, view='transition-activate')

        self.assertEqual('dossier-state-active',
                         api.content.get_state(self.dossier))
        self.assertEqual('dossier-state-active',
                         api.content.get_state(subdossier))
        self.assertEqual('dossier-state-active',
                         api.content.get_state(subsubdossier))

        self.assertEqual('The Dossier has been activated', info_messages()[0])

    @browsing
    def test_activating_a_subdossier_is_disallowed_when_main_dossier_is_inactive(self, browser):
        subdossier = create(Builder('dossier')
                            .within(self.dossier)
                            .in_state('dossier-state-inactive'))

        browser.login().open(subdossier, view='transition-activate')

        self.assertEqual('dossier-state-inactive',
                         api.content.get_state(subdossier))
        self.assertEqual("This subdossier can't be activated,"
                         "because the main dossiers is inactive",
                         error_messages()[0])
