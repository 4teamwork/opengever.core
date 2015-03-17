from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import MockTestCase
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.interfaces import IDossierResolver
from opengever.dossier.resolve import DossierResolver
from opengever.dossier.resolve import NO_START_DATE
from opengever.dossier.resolve import NOT_CHECKED_IN_DOCS
from opengever.dossier.resolve import NOT_CLOSED_TASKS
from opengever.dossier.resolve import NOT_SUPPLIED_OBJECTS
from opengever.dossier.resolve import ResolveConditions, Resolver
from opengever.testing import FunctionalTestCase
from plone.app.testing import applyProfile
from plone.protect import createToken
from zope.interface import implements
from zope.interface.verify import verifyClass


TEST_DATE = date(2012, 3, 1)


class TestResolvingDossiers(FunctionalTestCase):

    use_browser = True

    def setUp(self):
        super(TestResolvingDossiers, self).setUp()
        self.grant('Manager')

    def test_archive_form_is_omitted_for_sites_without_filing_number_support(self):
        dossier = create(Builder('dossier')
                         .having(start=date(2013, 11, 5)))

        self.browser.open(
            '{}/transition-resolve?_authenticator={}'.format(
                dossier.absolute_url(), createToken()))

        self.browser.assert_url(dossier.absolute_url())
        self.browser.assert_portal_message(
            'The dossier has been succesfully resolved')

    def test_archive_form_is_omitted_when_resolving_subdossiers(self):
        dossier = create(Builder('dossier'))
        subdossier = create(Builder('dossier')
                            .within(dossier)
                            .having(start=date(2013, 11, 5)))

        self.browser.open(
            '{}/transition-resolve?_authenticator={}'.format(
                subdossier.absolute_url(), createToken()))

        self.browser.assert_url(subdossier.absolute_url())
        self.browser.assert_portal_message(
            'The subdossier has been succesfully resolved')


class TestResolvingDossiersWithFilingNumberSupport(FunctionalTestCase):

    use_browser = True

    def setUp(self):
        super(TestResolvingDossiersWithFilingNumberSupport, self).setUp()

        applyProfile(self.portal, 'opengever.dossier:filing')
        self.grant('Manager')

    def test_archive_form_is_displayed_for_sites_with_filing_number_support(self):

        dossier = create(Builder('dossier')
                         .having(start=date(2013, 11, 5)))

        self.browser.open(
            '{}/transition-resolve?_authenticator={}'.format(
                dossier.absolute_url(), createToken()))

        self.browser.assert_url(
            '{}/transition-archive'.format(dossier.absolute_url()))


class TestResolveConditions(MockTestCase):

    def test_check_preconditions(self):

        context = self.stub()

        with self.mocker.order():
            self.expect(context.is_all_supplied()).result(False)
            self.expect(context.is_all_checked_in()).result(False)
            self.expect(context.is_all_closed()).result(True)
            self.expect(context.has_valid_startdate()).result(True)

            self.expect(context.is_all_supplied()).result(True)
            self.expect(context.is_all_checked_in()).result(True)
            self.expect(context.is_all_closed()).result(False)
            self.expect(context.has_valid_startdate()).result(True)

            self.expect(context.is_all_supplied()).result(True)
            self.expect(context.is_all_checked_in()).result(True)
            self.expect(context.is_all_closed()).result(True)
            self.expect(context.has_valid_startdate()).result(False)

            self.expect(context.is_all_supplied()).result(True)
            self.expect(context.is_all_checked_in()).result(True)
            self.expect(context.is_all_closed()).result(True)
            self.expect(context.has_valid_startdate()).result(True)

        self.replay()

        self.assertEquals(
            ResolveConditions(context).check_preconditions(),
            [NOT_SUPPLIED_OBJECTS, NOT_CHECKED_IN_DOCS]
            )

        self.assertEquals(
            ResolveConditions(context).check_preconditions(),
            [NOT_CLOSED_TASKS, ]
            )

        self.assertEquals(
            ResolveConditions(context).check_preconditions(),
            [NO_START_DATE]
            )

        self.assertEquals(
            ResolveConditions(context).check_preconditions(),
            []
            )

    def test_check_end_dates(self):
        dossier = self.stub()
        self.expect(dossier.title).result('Dossier')
        sub1 = self.stub()
        self.expect(sub1.title).result('Sub 1')
        self.expect(sub1.getObject()).result(sub1)
        sub2 = self.stub()
        self.expect(sub2.title).result('Sub 2')
        self.expect(sub2.getObject()).result(sub2)
        subsub1 = self.stub()
        self.expect(subsub1.title).result('Sub Sub 1')
        self.expect(subsub1.getObject()).result(subsub1)
        subsub2 = self.stub()
        self.expect(subsub2.title).result('Sub Sub 2')
        self.expect(subsub2.getObject()).result(subsub2)
        subsubsub1 = self.stub()
        self.expect(subsubsub1.title).result('Sub Sub Sub 1')
        self.expect(subsubsub1.getObject()).result(subsubsub1)

        with self.mocker.order():
            # test 1
            self.expect(dossier.get_subdossiers()).result([sub1, sub2])

            self.expect(sub1.has_valid_enddate()).result(False)
            self.expect(sub1.get_subdossiers()).result([subsub1, ])
            self.expect(subsub1.has_valid_enddate()).result(True)
            self.expect(subsub1.get_subdossiers()).result([])

            self.expect(sub2.has_valid_enddate()).result(True)
            self.expect(sub2.get_subdossiers()).result([subsub2, ])
            self.expect(subsub2.has_valid_enddate()).result(True)
            self.expect(subsub2.get_subdossiers()).result([subsubsub1, ])
            self.expect(subsubsub1.has_valid_enddate()).result(False)
            self.expect(subsubsub1.get_subdossiers()).result([])

            # test 2
            self.expect(dossier.get_subdossiers()).result([sub1, sub2])

            self.expect(sub1.has_valid_enddate()).result(True)
            self.expect(sub1.get_subdossiers()).result([subsub1, ])
            self.expect(subsub1.has_valid_enddate()).result(True)
            self.expect(subsub1.get_subdossiers()).result([])

            self.expect(sub2.has_valid_enddate()).result(True)
            self.expect(sub2.get_subdossiers()).result([subsub2, ])
            self.expect(subsub2.has_valid_enddate()).result(True)
            self.expect(subsub2.get_subdossiers()).result([subsubsub1, ])
            self.expect(subsubsub1.has_valid_enddate()).result(True)
            self.expect(subsubsub1.get_subdossiers()).result([])

            # test 3
            self.expect(dossier.get_subdossiers()).result([])

        self.replay()

        self.assertEquals(ResolveConditions(dossier).check_end_dates(),
            ['Sub 1', 'Sub Sub Sub 1']
            )
        self.assertEquals(ResolveConditions(dossier).check_end_dates(), [])
        self.assertEquals(ResolveConditions(dossier).check_end_dates(), [])


class TestResolver(MockTestCase):

    def test_implements_interface(self):
        verifyClass(IDossierResolver, DossierResolver)

    def test_resolve_dossier(self):

        wft = self.stub()
        self.mock_tool(wft, 'portal_workflow')

        # provide IDossier instead of IDossierMarker
        # so that zope.component doesn't lookup the adapter
        # and return the adapted object directly

        class StubDossier(object):
            implements(IDossier)

            def __init__(self, end, valid, sub=[]):
                self.end = end
                self.valid = valid
                self.sub = sub

            def getObject(self):
                return self

            def get_subdossiers(self):
                return self.sub

            def has_valid_enddate(self):
                return self.valid

        sub1 = StubDossier(date(2012, 1, 1), False)
        sub2 = StubDossier(date(2012, 2, 1), True)
        dossier = StubDossier(None, True, )
        subsub1 = StubDossier(None, False)

        dossier.sub = [sub1, sub2]
        sub1.sub = [subsub1, ]

        with self.mocker.order():
            # test 1
            self.expect(wft.getInfoFor(subsub1, 'review_state')).result(
                'dossier-state-active')
            self.expect(wft.doActionFor(subsub1, 'dossier-transition-resolve'))
            self.expect(wft.getInfoFor(sub1, 'review_state')).result(
                'dossier-state-active')
            self.expect(wft.doActionFor(sub1, 'dossier-transition-resolve'))
            self.expect(wft.getInfoFor(sub2, 'review_state')).result(
                'dossier-state-resolved')
            self.expect(wft.getInfoFor(dossier, 'review_state')).result(
                'dossier-state-active')
            self.expect(wft.doActionFor(dossier, 'dossier-transition-resolve'))

        self.replay()

        Resolver(dossier).resolve_dossier(TEST_DATE)
        self.assertEquals(dossier.end, TEST_DATE)
        self.assertEquals(sub1.end, TEST_DATE)
        self.assertEquals(sub2.end, date(2012, 2, 1))

    def test_resolving_subdossier(self):
        wft = self.stub()
        self.mock_tool(wft, 'portal_workflow')

        subdossier = self.providing_stub([IDossier, ])
        self.expect(subdossier.is_subdossier()).result(True)
        self.expect(subdossier.earliest_possible_end_date()).result(TEST_DATE)
        self.expect(subdossier.get_subdossiers()).result([])
        self.expect(wft.getInfoFor(subdossier, 'review_state')).result(
            'dossier-state-active')
        self.expect(wft.doActionFor(subdossier, 'dossier-transition-resolve'))

        self.replay()

        Resolver(subdossier).resolve_dossier()

        self.assertEquals(IDossier(subdossier).end, TEST_DATE)
