from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from opengever.testing import FunctionalTestCase


class TestBusinessCaseDossierIntegration(FunctionalTestCase):

    @browsing
    def test_deactivate_fails_with_resolved_subdossier(self, browser):
        dossier = create(Builder('dossier'))
        subdossier = create(Builder('dossier')
                            .within(dossier)
                            .titled(u'b\xe4\xe4\xe4h')
                            .in_state('dossier-state-resolved'))

        browser.login().open(dossier, view='transition-deactivate')
        self.assertEqual(
            u"The Dossier can't be deactivated, the subdossier b\xe4\xe4\xe4h is already resolved",
            error_messages()[0])
