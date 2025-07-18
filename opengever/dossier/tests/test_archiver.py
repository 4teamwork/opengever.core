from datetime import date
from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from ftw.testing import freeze
from opengever.base.behaviors.changed import IChanged
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.dossier.archive import Archiver
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.filing import IFilingNumber
from opengever.dossier.filing.form import EnddateValidator
from opengever.dossier.filing.form import get_filing_actions
from opengever.dossier.filing.form import METHOD_FILING
from opengever.dossier.filing.form import METHOD_RESOLVING
from opengever.dossier.filing.form import METHOD_RESOLVING_AND_FILING
from opengever.dossier.filing.form import METHOD_RESOLVING_EXISTING_FILING
from opengever.dossier.filing.form import MissingValue
from opengever.dossier.filing.form import ONLY_NUMBER
from opengever.dossier.filing.form import ONLY_RESOLVE
from opengever.dossier.filing.form import RESOLVE_AND_NUMBER
from opengever.dossier.filing.form import RESOLVE_WITH_EXISTING_NUMBER
from opengever.dossier.filing.form import RESOLVE_WITH_NEW_NUMBER
from opengever.dossier.filing.form import valid_filing_year
from opengever.dossier.interfaces import IDossierArchiver
from opengever.testing import IntegrationTestCase
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface.verify import verifyClass
from zope.schema.interfaces import IDate
import json
import pytz


class TestArchiver(IntegrationTestCase):

    features = ('filing_number', )

    def test_implements_interface(self):
        verifyClass(IDossierArchiver, Archiver)

    def test_number_generation(self):
        self.login(self.dossier_responsible)
        self.assertEquals(
            'Hauptmandant-Department-2011-1',
            IDossierArchiver(self.dossier).generate_number('department', '2011'))

        self.assertEquals(
            'Hauptmandant-Department-2011-2',
            IDossierArchiver(self.dossier).generate_number('department', '2011'))

        self.assertEquals(
            'Hauptmandant-Administration-2011-1',
            IDossierArchiver(self.dossier).generate_number('administration', '2011'))

        self.assertEquals(
            'Hauptmandant-Administration-2011-2',
            IDossierArchiver(self.dossier).generate_number('administration', '2011'))

        self.assertEquals(
            'Hauptmandant-Administration-2012-1',
            IDossierArchiver(self.dossier).generate_number('administration', '2012'))

    def test_archiving(self):
        self.login(self.dossier_responsible)
        IDossierArchiver(self.dossier).archive('administration', '2013')

        self.assertEquals('Hauptmandant-Administration-2013-1',
                          IFilingNumber(self.dossier).filing_no)
        self.assertEquals('Hauptmandant-Administration-2013-1.1',
                          IFilingNumber(self.subdossier).filing_no)
        self.assertEquals('Hauptmandant-Administration-2013-1.2',
                          IFilingNumber(self.subdossier2).filing_no)

    def test_archiving_with_existing_number(self):
        self.login(self.dossier_responsible)
        number = 'FAKE NUMBER'
        IDossierArchiver(self.dossier).archive('administration', '2013',
                                               number=number)
        self.assertEquals('FAKE NUMBER',
                          IFilingNumber(self.dossier).filing_no)
        self.assertEquals('FAKE NUMBER.1',
                          IFilingNumber(self.subdossier).filing_no)
        self.assertEquals('FAKE NUMBER.2',
                          IFilingNumber(self.subdossier2).filing_no)

    def test_update_prefix(self):
        self.login(self.dossier_responsible)
        IDossierArchiver(self.dossier).update_prefix('FAKE PREFIX')
        self.assertEquals('FAKE PREFIX',
                          IDossier(self.dossier).filing_prefix)
        self.assertEquals('FAKE PREFIX',
                          IDossier(self.subdossier).filing_prefix)
        self.assertEquals('FAKE PREFIX',
                          IDossier(self.subdossier2).filing_prefix)

    def test_valid_filing_year(self):
        self.assertTrue(valid_filing_year(u'2012'))
        self.assertTrue(valid_filing_year('1995'))
        not_valid_years = [
            '-2012', '2012 ', '12.12.2012', 'sdfd', '500', '5000', None]
        for year in not_valid_years:
            with self.assertRaises(Invalid):
                valid_filing_year(year)


class TestArchiving(IntegrationTestCase):

    features = ('filing_number', )

    def test_end_date_validator(self):
        self.login(self.regular_user)

        self.assertEqual(
            date(2016, 8, 31),
            self.dossier.earliest_possible_end_date())

        validator = EnddateValidator(
            self.dossier, self.request, Interface, IDate, Interface)

        # invalid
        with self.assertRaises(Invalid):
            validator.validate(date(2016, 8, 10))

        with self.assertRaises(MissingValue):
            self.assertRaises(validator.validate(None))

        # valid
        validator.validate(date(2016, 8, 31))
        validator.validate(date(2016, 10, 10))

    def test_get_filing_actions(self):
        self.login(self.regular_user)

        # dossier not resolved yet without a filing no
        IFilingNumber(self.resolvable_dossier).filing_no = None

        actions = get_filing_actions(self.resolvable_dossier)
        self.assertEquals(actions.by_token.keys(),
                          [ONLY_RESOLVE, RESOLVE_AND_NUMBER])
        self.assertEquals(actions.by_value.keys(),
                          [METHOD_RESOLVING_AND_FILING, METHOD_RESOLVING])

        # dossier not resolved yet but with a invalid filing no
        IFilingNumber(self.resolvable_dossier).filing_no = 'FAKE_NUMBER'
        actions = get_filing_actions(self.resolvable_dossier)
        self.assertEquals(actions.by_token.keys(),
                          [ONLY_RESOLVE, RESOLVE_AND_NUMBER])
        self.assertEquals(actions.by_value.keys(),
                          [METHOD_RESOLVING_AND_FILING, METHOD_RESOLVING])

        # dossier not resolved yet but with a valid filing no
        IFilingNumber(self.resolvable_dossier).filing_no = u'Hauptmandant-Amt-2016-2'
        actions = get_filing_actions(self.resolvable_dossier)
        self.assertEquals(
            actions.by_token.keys(),
            [RESOLVE_WITH_EXISTING_NUMBER, RESOLVE_WITH_NEW_NUMBER])
        self.assertEquals(actions.by_value.keys(),
                          [METHOD_RESOLVING_AND_FILING, METHOD_RESOLVING_EXISTING_FILING])

        # dossier allready resolved but without filing
        self.set_workflow_state(
            'dossier-state-resolved', self.resolvable_dossier)
        IFilingNumber(self.resolvable_dossier).filing_no = None

        actions = get_filing_actions(self.resolvable_dossier)
        self.assertEquals(actions.by_token.keys(), [ONLY_NUMBER])
        self.assertEquals(actions.by_value.keys(), [METHOD_FILING])


class TestArchiveFormDefaults(IntegrationTestCase):

    features = ('filing_number', )

    def _get_form_date(self, browser, field_name):
        datestr = browser.css('#form-widgets-%s' % field_name).first.value
        return datetime.strptime(datestr, '%d.%m.%Y').date()

    @browsing
    def test_filing_prefix_default(self, browser):
        # Dossier has no filing_prefix set - default to None in archive form
        self.login(self.dossier_responsible, browser)
        browser.open(self.dossier, view='transition-archive')
        form_default = browser.css('#form-widgets-filing_prefix').first.value
        self.assertEqual('--NOVALUE--', form_default)

        # Dossier has a filing_prefix - default to that one in archive form
        IDossier(self.dossier).filing_prefix = 'department'
        browser.open(self.dossier, view='transition-archive')
        form_default = browser.css('#form-widgets-filing_prefix').first.value
        self.assertEqual('department', form_default)

    @browsing
    def test_filing_year_default(self, browser):
        self.login(self.dossier_responsible, browser)
        # Dossier without sub-objects - earliest possible end date is dossier
        # start date, filing_year should therefore default to this year
        browser.open(self.empty_dossier, view='transition-archive')
        form_default = browser.css('#form-widgets-filing_year').first.value
        self.assertEqual('2016', form_default)

        # Document with date newer than dossier start. Suggested filing_year
        # default should be that of the document (year of the youngest object)
        with freeze(datetime(2050, 1, 1)):
            doc = create(Builder('document')
                         .within(self.empty_dossier))
        browser.open(self.empty_dossier, view='transition-archive')
        form_default = browser.css('#form-widgets-filing_year').first.value
        self.assertEqual(doc.document_date.year, int(form_default))

    @browsing
    def test_enddate_may_be_latest_document_modification_date(self, browser):
        """When a document's modification date is greater than the dossier
        end date, use the document's modification date.
        """
        self.login(self.dossier_responsible, browser)
        IDossier(self.dossier).end = date(2021, 1, 1)
        self.dossier.reindexObject(idxs=['end'])

        IChanged(self.subdocument).changed = datetime(2021, 1, 2, tzinfo=pytz.utc)
        self.subdocument.reindexObject(idxs=['changed'])
        browser.open(self.dossier, view='transition-archive')
        self.assertEqual(date(2021, 1, 2),
                         self._get_form_date(browser, 'dossier_enddate'))

    @browsing
    def test_enddate_may_be_latest_document_date(self, browser):
        """When a document's date is greater than the dossier end date and the
        use_changed_for_end_date feature is deactivated, use the document's date.
        """
        self.deactivate_feature('changed_for_end_date')

        self.login(self.dossier_responsible, browser)
        IDossier(self.dossier).end = date(2021, 1, 1)
        self.dossier.reindexObject(idxs=['end'])

        IDocumentMetadata(self.subdocument).document_date = date(2021, 1, 2)
        self.subdocument.reindexObject(idxs=['document_date'])
        browser.open(self.dossier, view='transition-archive')
        self.assertEqual(date(2021, 1, 2),
                         self._get_form_date(browser, 'dossier_enddate'))

    @browsing
    def test_enddate_may_be_latest_dossier_end_date(self, browser):
        """When a dossiers end date is greater than the document's modification
        date, use the dossier end date.
        """
        self.login(self.dossier_responsible, browser)
        IDossier(self.dossier).end = date(2021, 2, 2)
        self.dossier.reindexObject(idxs=['end'])
        IChanged(self.subdocument).changed = datetime(2021, 1, 2, tzinfo=pytz.utc)
        self.subdocument.reindexObject(idxs=['changed'])
        browser.open(self.dossier, view='transition-archive')
        self.assertEqual(date(2021, 2, 2),
                         self._get_form_date(browser, 'dossier_enddate'))


class TestArchiveForm(IntegrationTestCase):

    features = ('filing_number', )

    @browsing
    def test_resolving_and_add_filing_number(self, browser):
        self.login(self.secretariat_user, browser)
        browser.open(self.empty_dossier, view='transition-archive')

        browser.fill({'Filing number prefix': 'Cantonal Government',
                      'Filing year': u'2017',
                      'Action': 'resolve and set filing no'})
        browser.click_on('Archive')

        self.assert_workflow_state(
            'dossier-state-resolved', self.empty_dossier)
        statusmessages.assert_message('Dossier has been resolved')
        self.assertEquals('Hauptmandant-Cantonal Government-2017-1',
                          IFilingNumber(self.empty_dossier).filing_no)

    @browsing
    def test_resolving_use_existing_filing_number(self, browser):
        self.login(self.secretariat_user, browser)

        former_filing_number = u'Hauptmandant-Administration-2013-1'
        IFilingNumber(self.empty_dossier).filing_no = former_filing_number
        browser.open(self.empty_dossier, view='transition-archive')

        browser.fill({'Filing number prefix': 'Cantonal Government',
                      'Filing year': u'2017',
                      'Action': 'resolve and take the existing filing no'})
        browser.click_on('Archive')

        self.assert_workflow_state(
            'dossier-state-resolved', self.empty_dossier)
        statusmessages.assert_message('Dossier has been resolved')
        self.assertEquals(former_filing_number,
                          IFilingNumber(self.empty_dossier).filing_no)

    @browsing
    def test_resolving_and_use_existing_filing_number(self, browser):
        self.login(self.secretariat_user, browser)

        former_filing_number = u'Hauptmandant-Administration-2013-1'
        IFilingNumber(self.empty_dossier).filing_no = former_filing_number
        browser.open(self.empty_dossier, view='transition-archive')

        browser.fill({'Filing number prefix': 'Cantonal Government',
                      'Filing year': u'2017',
                      'Action': 'resolve and take the existing filing no'})
        browser.click_on('Archive')

        self.assert_workflow_state(
            'dossier-state-resolved', self.empty_dossier)
        statusmessages.assert_message('Dossier has been resolved')
        self.assertEquals(former_filing_number,
                          IFilingNumber(self.empty_dossier).filing_no)

    @browsing
    def test_resolving_and_set_new_filing_number(self, browser):
        self.login(self.secretariat_user, browser)

        former_filing_number = u'Hauptmandant-Administration-2013-1'
        IFilingNumber(self.empty_dossier).filing_no = former_filing_number
        browser.open(self.empty_dossier, view='transition-archive')

        browser.fill({'Filing number prefix': 'Cantonal Government',
                      'Filing year': u'2017',
                      'Action': 'resolve and set a new filing no'})
        browser.click_on('Archive')

        self.assert_workflow_state(
            'dossier-state-resolved', self.empty_dossier)
        statusmessages.assert_message('Dossier has been resolved')
        self.assertEquals('Hauptmandant-Cantonal Government-2017-1',
                          IFilingNumber(self.empty_dossier).filing_no)

    @browsing
    def test_only_give_filing_number_on_resolved_dossier(self, browser):
        self.login(self.secretariat_user, browser)
        self.set_workflow_state('dossier-state-resolved', self.empty_dossier)
        browser.open(self.empty_dossier, view='transition-archive')

        browser.fill({'Filing number prefix': 'Cantonal Government',
                      'Filing year': u'2017',
                      'Action': 'set a filing no'})
        browser.click_on('Archive')

        self.assert_workflow_state(
            'dossier-state-resolved', self.empty_dossier)
        statusmessages.assert_message('Filing number issued.')
        self.assertEquals('Hauptmandant-Cantonal Government-2017-1',
                          IFilingNumber(self.empty_dossier).filing_no)

    @browsing
    def test_precondition_violation_raises_error_already_on_resolve_view(self, browser):
        """Make sure the resolve view catches failing preconditions before
        even redirecting to archive form.
        """
        self.login(self.secretariat_user, browser)

        # Create open task to violate one of the preconditions for resolving
        create(Builder('task')
               .within(self.empty_dossier)
               .having(responsible_client='fa',
                       responsible=self.regular_user.getId(),
                       issuer=self.dossier_responsible.getId(),
                       task_type='correction',
                       deadline=date(2016, 11, 1))
               .in_state('task-state-open'))

        # Resolve view will redirect to archive form if filing number feature
        # is enabled. But it should first check preconditions.
        browser.open(self.empty_dossier, view='transition-resolve')

        self.assert_workflow_state(
            'dossier-state-active', self.empty_dossier)
        self.assertEqual(['not all task are closed'],
                         statusmessages.error_messages())
        self.assertEqual(self.empty_dossier.absolute_url(), browser.url)

    @browsing
    def test_precondition_violation_raises_error_on_archive_form(self, browser):
        """Preconditions also need to be validated and handled correctly if
        the user directly invokes the transition-archive form.
        """
        self.login(self.secretariat_user, browser)

        # Create open task to violate one of the preconditions for resolving
        create(Builder('task')
               .within(self.empty_dossier)
               .having(responsible_client='fa',
                       responsible=self.regular_user.getId(),
                       issuer=self.dossier_responsible.getId(),
                       task_type='correction',
                       deadline=date(2016, 11, 1))
               .in_state('task-state-open'))

        browser.open(self.empty_dossier, view='transition-archive')

        browser.fill({'Filing number prefix': 'Cantonal Government',
                      'Filing year': u'2017',
                      'Action': 'resolve and set filing no'})
        browser.click_on('Archive')

        self.assert_workflow_state(
            'dossier-state-active', self.empty_dossier)
        self.assertEqual(['not all task are closed'],
                         statusmessages.error_messages())
        self.assertEquals(None,
                          IFilingNumber(self.empty_dossier).filing_no)

    @browsing
    def test_resolving_nested_dossier(self, browser):
        self.login(self.secretariat_user, browser)
        browser.open(self.resolvable_dossier, view='transition-archive')

        browser.fill({'Filing number prefix': 'Cantonal Government',
                      'Filing year': u'2018',
                      'Action': 'resolve and set filing no'})
        browser.click_on('Archive')

        self.assert_workflow_state(
            'dossier-state-resolved', self.resolvable_dossier)
        self.assert_workflow_state(
            'dossier-state-resolved', self.resolvable_subdossier)


class TestArchivePerAPI(IntegrationTestCase):

    features = ('filing_number', )

    raise_http_errors = False

    @browsing
    def test_resolving_and_add_filing_number(self, browser):
        self.login(self.secretariat_user, browser)

        data = {
            'filing_prefix': 'government',
            'filing_year': '2017',
            'filing_action': RESOLVE_AND_NUMBER,
            'dossier_enddate': '2017-01-01',
        }
        browser.open(self.empty_dossier, method="POST", headers=self.api_headers,
                     view='@workflow/dossier-transition-resolve',
                     data=json.dumps(data))

        self.assertEqual(200, browser.status_code)
        self.assert_workflow_state(
            'dossier-state-resolved', self.empty_dossier)
        self.assertEquals('Hauptmandant-Cantonal Government-2017-1',
                          IFilingNumber(self.empty_dossier).filing_no)

    @browsing
    def test_resolving_use_existing_filing_number(self, browser):
        self.login(self.secretariat_user, browser)

        former_filing_number = u'Hauptmandant-Administration-2013-1'
        IFilingNumber(self.empty_dossier).filing_no = former_filing_number

        data = {'filing_prefix': 'government',
                'filing_year': u'2017',
                'dossier_enddate': '2017-01-01',
                'filing_action': METHOD_RESOLVING_EXISTING_FILING}

        browser.open(self.empty_dossier, method="POST", headers=self.api_headers,
                     view='@workflow/dossier-transition-resolve',
                     data=json.dumps(data))

        self.assert_workflow_state('dossier-state-resolved', self.empty_dossier)
        self.assertEqual(200, browser.status_code)
        self.assertEquals(former_filing_number,
                          IFilingNumber(self.empty_dossier).filing_no)

    @browsing
    def test_resolving_and_set_new_filing_number(self, browser):
        self.login(self.secretariat_user, browser)

        former_filing_number = u'Hauptmandant-Administration-2013-1'
        IFilingNumber(self.empty_dossier).filing_no = former_filing_number

        data = {'filing_prefix': 'government',
                'filing_year': u'2017',
                'dossier_enddate': '2017-01-01',
                'filing_action': METHOD_RESOLVING_AND_FILING}

        browser.open(self.empty_dossier, method="POST", headers=self.api_headers,
                     view='@workflow/dossier-transition-resolve',
                     data=json.dumps(data))

        self.assert_workflow_state(
            'dossier-state-resolved', self.empty_dossier)
        self.assertEqual(200, browser.status_code)
        self.assertEquals('Hauptmandant-Cantonal Government-2017-1',
                          IFilingNumber(self.empty_dossier).filing_no)

    @browsing
    def test_precondition_violation_raises_error_already_on_resolve_view(self, browser):
        """Make sure the resolve view catches failing preconditions before
        even redirecting to archive form.
        """
        self.login(self.secretariat_user, browser)

        # Create open task to violate one of the preconditions for resolving
        create(Builder('task')
               .within(self.empty_dossier)
               .having(responsible_client='fa',
                       responsible=self.regular_user.getId(),
                       issuer=self.dossier_responsible.getId(),
                       task_type='correction',
                       deadline=date(2016, 11, 1))
               .in_state('task-state-open'))

        data = {'filing_prefix': 'government',
                'filing_year': u'2017',
                'dossier_enddate': '2017-01-01',
                'filing_action': METHOD_RESOLVING_AND_FILING}

        with browser.expect_http_error(code=400):
            browser.open(self.empty_dossier, method="POST",
                         headers=self.api_headers,
                         view='@workflow/dossier-transition-resolve',
                         data=json.dumps(data))

        self.assertEqual(
            {u'error': {
                u'message': u'',
                u'errors': [u'not all task are closed'],
                u'has_not_closed_tasks': True,
                u'type': u'PreconditionsViolated'}},
            browser.json)

    @browsing
    def test_resolving_nested_dossier(self, browser):
        self.login(self.secretariat_user, browser)

        data = {
            'filing_prefix': 'government',
            'filing_year': '2017',
            'filing_action': RESOLVE_AND_NUMBER,
            'dossier_enddate': '2017-01-01',
        }
        browser.open(self.resolvable_dossier, method="POST", headers=self.api_headers,
                     view='@workflow/dossier-transition-resolve',
                     data=json.dumps(data))

        self.assertEqual(200, browser.status_code)

        self.assert_workflow_state(
            'dossier-state-resolved', self.resolvable_dossier)
        self.assert_workflow_state(
            'dossier-state-resolved', self.resolvable_subdossier)

    @browsing
    def test_resolving_subdossier_does_not_require_filing_informations(self, browser):
        self.login(self.secretariat_user, browser)
        browser.open(self.subdossier, method="POST", headers=self.api_headers,
                     view='@workflow/dossier-transition-resolve')

        self.assertEqual(200, browser.status_code)

        self.assert_workflow_state('dossier-state-resolved', self.subdossier)
