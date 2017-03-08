from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from ftw.testbrowser.pages.statusmessages import warning_messages
from opengever.testing import FunctionalTestCase
from plone import api
from plone.protect import createToken


class TestReactivating(FunctionalTestCase):

    def setUp(self):
        super(TestReactivating, self).setUp()
        self.grant('Reader', 'Contributor', 'Editor', 'Reviewer', 'Publisher')

    @browsing
    def test_reactivating_a_resolved_dossier_succesfully(self, browser):
        dossier = create(Builder('dossier')
                         .in_state('dossier-state-resolved'))

        browser.login().open(dossier)
        browser.click_on('dossier-transition-reactivate')

        self.assertEquals('dossier-state-active',
                          api.content.get_state(dossier))
        self.assertEquals(['Dossiers successfully reactivated.'],
                          info_messages())

    @browsing
    def test_reactivating_a_main_dossier_reactivates_subdossiers_recursively(self, browser):
        dossier = create(Builder('dossier')
                         .in_state('dossier-state-resolved'))
        sub = create(Builder('dossier')
                     .within(dossier)
                     .in_state('dossier-state-resolved'))
        subsub = create(Builder('dossier')
                        .within(sub)
                        .in_state('dossier-state-resolved'))

        browser.login().open(dossier, view=u'transition-reactivate',
                             data={'_authenticator': createToken()})
        self.assertEquals('dossier-state-active',
                          api.content.get_state(dossier))
        self.assertEquals('dossier-state-active',
                          api.content.get_state(sub))
        self.assertEquals('dossier-state-active',
                          api.content.get_state(subsub))

    @browsing
    def test_reactivating_a_subdossier_of_a_resolved_dossier_is_not_possible(self, browser):
        dossier = create(Builder('dossier')
                         .in_state('dossier-state-resolved'))
        sub = create(Builder('dossier')
                     .within(dossier)
                     .in_state('dossier-state-resolved'))

        browser.login().open(sub, view=u'transition-reactivate',
                             data={'_authenticator': createToken()})

        self.assertEquals(
            ["It isn't possible to reactivate a sub dossier."],
            warning_messages())
        self.assertEquals('dossier-state-resolved', api.content.get_state(sub))
