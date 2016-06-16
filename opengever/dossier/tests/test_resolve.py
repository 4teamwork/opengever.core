from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import error_messages
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import applyProfile
from plone.protect import createToken


class TestResolvingDossiers(FunctionalTestCase):

    @browsing
    def test_archive_form_is_omitted_for_sites_without_filing_number_support(self, browser):
        self.grant('Manager')
        dossier = create(Builder('dossier')
                         .having(start=date(2013, 11, 5)))

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertEquals(dossier.absolute_url(), browser.url)
        self.assertEquals(['The dossier has been succesfully resolved'],
                          info_messages())

    @browsing
    def test_archive_form_is_omitted_when_resolving_subdossiers(self, browser):
        self.grant('Manager')
        dossier = create(Builder('dossier'))
        subdossier = create(Builder('dossier')
                            .within(dossier)
                            .having(start=date(2013, 11, 5)))

        browser.login().open(subdossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertEquals(subdossier.absolute_url(), browser.url)
        self.assertEquals(['The subdossier has been succesfully resolved'],
                          info_messages())


class TestResolvingDossiersWithFilingNumberSupport(FunctionalTestCase):

    def setUp(self):
        super(TestResolvingDossiersWithFilingNumberSupport, self).setUp()

        applyProfile(self.portal, 'opengever.dossier:filing')

    @browsing
    def test_archive_form_is_displayed_for_sites_with_filing_number_support(self, browser):
        dossier = create(Builder('dossier')
                         .having(start=date(2013, 11, 5)))

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')
        self.assertEquals(
            '{}/transition-archive'.format(dossier.absolute_url()),
            browser.url)


class TestResolveConditions(FunctionalTestCase):

    def setUp(self):
        super(TestResolveConditions, self).setUp()
        self.grant('Contributor', 'Editor', 'Reader', 'Reviewer')

    @browsing
    def test_resolving_is_cancelled_when_documents_are_not_filed_correctly(self, browser):
        dossier = create(Builder('dossier'))
        create(Builder('dossier').within(dossier))
        create(Builder('document').within(dossier).checked_out())

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertEquals(dossier.absolute_url(), browser.url)
        self.assertEquals(
            ['not all documents and tasks are stored in a subdossier',
             'not all documents are checked in'], error_messages())

    @browsing
    def test_resolving_is_cancelled_when_documents_are_checked_out(self, browser):
        dossier = create(Builder('dossier'))
        create(Builder('document').within(dossier).checked_out())

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertEquals(dossier.absolute_url(), browser.url)
        self.assertEquals(['not all documents are checked in'],
                          error_messages())

    @browsing
    def test_resolving_is_cancelled_when_active_tasks_exist(self, browser):
        dossier = create(Builder('dossier'))
        create(Builder('task').within(dossier))

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertEquals(dossier.absolute_url(), browser.url)
        self.assertEquals(['not all task are closed'],
                          error_messages())

    @browsing
    def test_resolving_is_cancelled_when_dossier_has_an_invalid_end_date(self, browser):
        dossier = create(Builder('dossier').having(end=date(2016, 5, 7)))
        create(Builder('document')
               .within(dossier)
               .having(document_date=date(2016, 6, 1)))


        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertEquals(dossier.absolute_url(), browser.url)
        self.assertEquals([],
                          error_messages())

    @browsing
    def test_resolving_is_cancelled_when_dossier_has_active_proposals(self, browser):
        repo = create(Builder('repository'))
        dossier = create(Builder('dossier')
                         .within(repo)
                         .having(end=date(2016, 5, 7)))
        create(Builder('proposal').within(dossier))

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertEquals(dossier.absolute_url(), browser.url)
        self.assertEquals(['The dossier contains active proposals.'],
                          error_messages())

    @browsing
    def test_dossier_is_resolved_when_all_tasks_are_closed_and_documents_checked_in(self, browser):
        dossier = create(Builder('dossier'))
        create(Builder('document').within(dossier))
        create(Builder('task').within(dossier)
               .in_state('task-state-tested-and-closed'))

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertEquals(dossier.absolute_url(), browser.url)
        self.assertEquals(['The dossier has been succesfully resolved'],
                          info_messages())


class TestResolving(FunctionalTestCase):

    def setUp(self):
        super(TestResolving, self).setUp()
        self.grant('Contributor', 'Editor', 'Reader', 'Reviewer')

    @browsing
    def test_set_end_date_to_earliest_possible_one(self, browser):
        dossier = create(Builder('dossier').having(start=date(2015, 1, 1)))
        subdossier = create(Builder('dossier')
                            .having(start=date(2015, 1, 1))
                            .within(dossier))
        create(Builder('document')
               .within(subdossier)
               .having(document_date=date(2016, 6, 1)))

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertEquals(date(2016, 6, 1), IDossier(dossier).end)
        self.assertEquals(date(2016, 6, 1), IDossier(subdossier).end,
                          'The end date has not been set recursively.')

    @browsing
    def test_resolves_the_dossier_and_subdossiers(self, browser):
        dossier = create(Builder('dossier'))
        subdossier = create(Builder('dossier').within(dossier))

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(dossier))
        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(subdossier))

    @browsing
    def test_handles_already_resolved_subdossiers(self, browser):
        dossier = create(Builder('dossier'))
        subdossier = create(Builder('dossier')
                            .within(dossier)
                            .in_state('dossier-state-resolved'))

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(dossier))
        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(subdossier))

    @browsing
    def test_inactive_subdossiers_stays_inactive(self, browser):
        dossier = create(Builder('dossier'))
        subdossier = create(Builder('dossier')
                            .within(dossier)
                            .in_state('dossier-state-inactive'))

        browser.login().open(dossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(dossier))
        self.assertEquals('dossier-state-inactive',
                          api.content.get_state(subdossier))

    @browsing
    def test_resolving_only_a_subdossier_is_possible(self, browser):
        dossier = create(Builder('dossier'))
        subdossier = create(Builder('dossier').within(dossier))

        browser.login().open(subdossier,
                             {'_authenticator': createToken()},
                             view='transition-resolve')

        self.assertEquals('dossier-state-active',
                          api.content.get_state(dossier))
        self.assertEquals('dossier-state-resolved',
                          api.content.get_state(subdossier))
