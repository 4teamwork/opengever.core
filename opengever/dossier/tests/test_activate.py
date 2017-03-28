from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.core.testing import OPENGEVER_FUNCTIONAL_TESTING_POSTGRES
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import FunctionalTestCase
from plone import api
from plone.protect import createToken


class TestDossierActivation(FunctionalTestCase):
    # This test uses the postgres layer in order to profe that postgres can
    # be used in tests. It was chose randomly.
    # The layer should be removed when "FunctionalTestCase" has been switched
    # to postgres testing as default.
    layer = OPENGEVER_FUNCTIONAL_TESTING_POSTGRES

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

        browser.login().open(self.dossier, view='transition-activate',
                             data={'_authenticator': createToken()})

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

        browser.login().open(subdossier, view='transition-activate',
                             data={'_authenticator': createToken()})

        self.assertEqual('dossier-state-inactive',
                         api.content.get_state(subdossier))
        self.assertEqual("This subdossier can't be activated,"
                         "because the main dossiers is inactive",
                         error_messages()[0])

    @browsing
    def test_resets_end_dates_recursively(self, browser):
        dossier = create(Builder('dossier')
                         .having(end=date(2013, 2, 21))
                         .in_state('dossier-state-inactive'))
        sub = create(Builder('dossier')
                     .within(dossier)
                     .having(end=date(2013, 2, 21))
                     .in_state('dossier-state-inactive'))
        subsub = create(Builder('dossier')
                        .within(sub)
                        .having(end=date(2013, 2, 21))
                        .in_state('dossier-state-inactive'))

        browser.login().open(dossier, view=u'transition-activate',
                             data={'_authenticator': createToken()})

        self.assertIsNone(IDossier(dossier).end)
        self.assertIsNone(IDossier(sub).end)
        self.assertIsNone(IDossier(subsub).end)
