from datetime import date
from datetime import datetime
from DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from ftw.pdfgenerator.builder import Builder as PDFBuilder
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.pdfgenerator.utils import provide_request_layer
from ftw.testbrowser import browsing
from ftw.testing import freeze
from lxml.cssselect import CSSSelector
from opengever.base.interfaces import IReferenceNumberSettings
from opengever.base.response import IResponseContainer
from opengever.latex.layouts.default import DefaultLayout
from opengever.latex.listing import ILaTexListing
from opengever.latex.tasklisting import ITaskListingLayer
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2brain
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
import json
import lxml


class BaseLatexListingTest(FunctionalTestCase):

    def assert_row_values(self, expected, row):
        self.assertEquals(
            expected,
            [value.text_content().strip() for value in
             row.xpath(CSSSelector('td').path)])


class TestDossierListing(BaseLatexListingTest):

    def setUp(self):
        super(TestDossierListing, self).setUp()

        self.hugo = create(Builder('fixture').with_hugo_boss())

        self.repo = create(Builder('repository').titled('Main Repository '))
        self.subrepo = create(Builder('repository')
                              .within(self.repo)
                              .titled('Repository XY'))
        self.dossier = create(Builder('dossier')
                          .within(self.subrepo)
                          .having(title=u'Dossier A',
                                  responsible=self.hugo.userid,
                                  start=date(2013, 11, 1),
                                  end=date(2013, 12, 31))
                          .in_state('dossier-state-resolved'))
        self.subdossier = create(Builder('dossier')
                                 .within(self.dossier)
                          .having(title=u'Dossier B',
                                  start=date(2013, 11, 1),
                                  responsible=self.hugo.userid))

        self.listing = getMultiAdapter(
            (self.subrepo, self.subrepo.REQUEST, self),
            ILaTexListing, name='dossiers')

    def test_get_responsible_returns_client_title_and_user_description(self):

        responsible = self.listing.get_responsible(
            obj2brain(self.dossier))

        self.assertEquals(u'Admin Unit 1 / Boss Hugo (hugo.boss)', responsible)

    def test_get_repository_title_returns_the_title_of_the_first_parental_repository_folder(self):
        self.assertEquals(
            '1.1. Repository XY',
            self.listing.get_repository_title(obj2brain(self.dossier)))

        self.assertEquals(
            '1.1. Repository XY',
            self.listing.get_repository_title(
                obj2brain(self.subdossier)))

    def test_configured_width_is_set_in_the_colgroup(self):
        self.listing.items = [obj2brain(self.dossier),
                               obj2brain(self.subdossier)]

        table = lxml.html.fromstring(self.listing.template())
        cols = table.xpath(CSSSelector('col').path)

        self.assertEquals(
            ['10%', '5%', '20%', '25%', '20%', '10%', '5%', '5%'],
            [col.get('width') for col in cols])

    def test_labels_are_translated_and_show_as_table_headers(self):
        self.listing.items = [obj2brain(self.dossier),
                               obj2brain(self.subdossier)]

        table = lxml.html.fromstring(self.listing.template())
        cols = table.xpath(CSSSelector('thead th').path)

        self.assertEquals(
            ['Reference number', 'No.', 'Repository folder', 'Title',
             'Responsible', 'State', 'Start', 'End'],
            [col.text_content().strip() for col in cols])

    def test_full_values_rendering(self):
        self.listing.items = [obj2brain(self.dossier),
                               obj2brain(self.subdossier)]

        table = lxml.html.fromstring(self.listing.template())
        rows = table.xpath(CSSSelector('tbody tr').path)

        self.assert_row_values(
            ['Client1 1.1 / 1',
             '1',
             '1.1. Repository XY',
             'Dossier A',
             'Admin Unit 1 / Boss Hugo (hugo.boss)',
             'Resolved',
             '01.11.2013',
             '31.12.2013'], rows[0])

        self.assert_row_values(
            ['Client1 1.1 / 1.1',
             '2',
             '1.1. Repository XY',
             'Dossier B',
             'Admin Unit 1 / Boss Hugo (hugo.boss)',
             'Active',
             '01.11.2013',
             ''], rows[1])


class TestDossierListingWithGrouppedByThreeFormatter(BaseLatexListingTest):

    def setUp(self):
        super(TestDossierListingWithGrouppedByThreeFormatter, self).setUp()

        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IReferenceNumberSettings)
        proxy.formatter = 'grouped_by_three'

        self.repo = create(Builder('repository').titled('Main Repository'))
        self.subrepo = create(Builder('repository')
                              .within(self.repo)
                              .titled('Repository XY'))
        self.dossier = create(Builder('dossier')
                              .within(self.subrepo)
                              .having(title=u'Dossier A'))
        self.subdossier = create(Builder('dossier')
                                 .within(self.dossier)
                                 .having(title=u'Dossier B'))

        self.listing = getMultiAdapter(
            (self.subrepo, self.subrepo.REQUEST, self),
            ILaTexListing, name='dossiers')

    def test_get_repository_title_returns_the_title_of_the_first_parental_repository_folder(self):
        self.assertEquals(
            '11 Repository XY',
            self.listing.get_repository_title(obj2brain(self.dossier)))

        self.assertEquals(
            '11 Repository XY',
            self.listing.get_repository_title(
                obj2brain(self.subdossier)))


class TestSubDossierListing(BaseLatexListingTest):

    def setUp(self):
        super(TestSubDossierListing, self).setUp()

        self.hugo = create(Builder('fixture').with_hugo_boss())

        self.repo = create(Builder('repository').titled('Repository XY'))
        self.dossier = create(Builder('dossier')
                          .within(self.repo)
                          .having(title=u'Dossier A',
                                  responsible=self.hugo.userid,
                                  start=date(2013, 11, 1),
                                  end=date(2013, 12, 31))
                          .in_state('dossier-state-resolved'))

        self.listing = getMultiAdapter(
            (self.repo, self.repo.REQUEST, self),
            ILaTexListing, name='subdossiers')

    def test_labels_are_translated_and_show_as_table_headers(self):
        self.listing.items = [obj2brain(self.dossier)]

        table = lxml.html.fromstring(self.listing.template())
        cols = table.xpath(CSSSelector('thead th').path)

        self.assertEquals(
            ['No.', 'Title', 'Responsible', 'State', 'Start', 'End'],
            [col.text_content().strip() for col in cols])

        cols = table.xpath(CSSSelector('colgroup col').path)
        self.assertEquals(
            ['5%', '40%', '33%', '10%', '6%', '6%'],
            [col.get('width') for col in cols])

    def test_drop_reference_from_default_dossier_listings(self):
        self.listing.items = [obj2brain(self.dossier)]

        table = lxml.html.fromstring(self.listing.template())
        rows = table.xpath(CSSSelector('tbody tr').path)

        self.assert_row_values(
            ['1',
             'Dossier A',
             'Admin Unit 1 / Boss Hugo (hugo.boss)',
             'Resolved',
             '01.11.2013',
             '31.12.2013'], rows[0])


class TestCommentsListing(BaseLatexListingTest):

    def setUp(self):
        super(TestCommentsListing, self).setUp()
        self.hugo = create(Builder('fixture').with_hugo_boss())
        self.repo = create(Builder('repository').titled('Repository XY'))
        self.dossier = create(Builder('dossier')
                              .having(title=u'Dossier A',
                                      responsible=self.hugo.userid,
                                      start=date(2013, 11, 1),
                                      end=date(2013, 12, 31)))
        self.api_headers = {'Accept': 'application/json',
                            'Content-Type': 'application/json'}

        self.listing = getMultiAdapter(
            (self.dossier, self.dossier.REQUEST, self),
            ILaTexListing, name='comments')

    @browsing
    def test_comments_listing(self, browser):
        with freeze(datetime(2016, 12, 9, 9, 40)) as clock:
            browser.login().open(self.dossier, view='@responses', method="POST",
                                 headers=self.api_headers,
                                 data=json.dumps({'text': u'Angebot \xfcberpr\xfcft'}))
            clock.forward(days=4, hours=3)
            browser.login().open(self.dossier, view='@responses', method="POST",
                                 headers=self.api_headers,
                                 data=json.dumps({'text': u'Angebot korrigiert'}))
            self.listing.items = IResponseContainer(self.dossier).list()
            table = lxml.html.fromstring(self.listing.template())
            rows = table.xpath(CSSSelector('tbody tr').path)
            cols = table.xpath(CSSSelector('thead th').path)

            self.assertEqual(['Time', 'Created by', 'Comment'], [
                             col.text_content().strip() for col in cols])
            self.assert_row_values(
                ['09.12.2016 09:40', 'Test User (test_user_1_)', u'Angebot \xfcberpr\xfcft'],
                rows[0])
            self.assert_row_values(
                ['13.12.2016 12:40', 'Test User (test_user_1_)', 'Angebot korrigiert'],
                rows[1])


class TestDocumentListing(BaseLatexListingTest):

    def setUp(self):
        super(TestDocumentListing, self).setUp()

        self.document = create(Builder('document')
                               .having(title=u'Document A',
                                       document_date=date(2013, 11, 4),
                                       receipt_date=date(2013, 11, 6),
                                       document_author='Hugo Boss'))

        self.listing = getMultiAdapter(
            (self.document, self.document.REQUEST, self),
            ILaTexListing, name='documents')

    def test_drop_reference_and_sequence_number_from_default_dossier_listings(self):
        self.listing.items = [obj2brain(self.document)]

        table = lxml.html.fromstring(self.listing.template())
        rows = table.xpath(CSSSelector('tbody tr').path)

        self.assert_row_values(
            ['1',
             'Document A',
             '04.11.2013',
             '06.11.2013',
             '',
             'Hugo Boss'], rows[0])


class TestTaskListings(BaseLatexListingTest):

    def setUp(self):
        super(TestTaskListings, self).setUp()

        self.hugo = create(Builder('fixture').with_hugo_boss())

        self.org_unit_2 = create(Builder('org_unit').id('org-unit-2')
                                 .having(admin_unit=self.admin_unit))

        self.task = create(Builder('task')
                           .having(
                               title='Task A',
                               task_type='approval',
                               responsible=self.hugo.userid,
                               responsible_client=self.org_unit.id(),
                               issuer=self.hugo.userid,
                               deadline=date(2013, 11, 6))
                           .in_state('task-state-in-progress'))

        self.listing = getMultiAdapter(
            (self.task, self.task.REQUEST, self),
            ILaTexListing, name='tasks')

    def test_labels_are_translated_and_show_as_table_headers(self):
        self.listing.items = [self.task.get_sql_object(),
                               self.task.get_sql_object()]

        table = lxml.html.fromstring(self.listing.template())
        cols = table.xpath(CSSSelector('thead th').path)

        self.assertEquals(
            ['No.', 'Task type', 'Issuer', 'Responsible',
             'State', 'Title', 'Deadline'],
            [col.text_content().strip() for col in cols])

    def test_drop_reference_and_sequence_number_from_default_task_listings(self):
        self.listing.items = [self.task.get_sql_object()]

        table = lxml.html.fromstring(self.listing.template())
        rows = table.xpath(CSSSelector('tbody tr').path)

        self.assert_row_values(
            ['1',
             'For your approval',
             'Org Unit 1 / Boss Hugo',
             'Org Unit 1 / Boss Hugo',
             'In progress',
             'Task A',
             '06.11.2013'], rows[0])

    @browsing
    def test_task_listing(self, browser):
        task_id = self.task.get_sql_object().id
        browser.login().open(data={'pdf-tasks-listing:method': 1,
                                   'task_ids:list': task_id})


class TestTaskListingLaTeXView(IntegrationTestCase):

    def test_task_listing_latex_view_shows_main_task(self):
        self.login(self.regular_user)
        subsubtask = create(Builder('task')
                            .titled(u'My Subsubtask')
                            .having(issuer=self.dossier_responsible.id,
                                    responsible=self.regular_user.id,
                                    responsible_client='fa',
                                    task_type='information')
                            .within(self.subtask))
        provide_request_layer(self.request, ITaskListingLayer)
        self.request.form['tasks'] = [
            self.task.absolute_url(), self.subtask.absolute_url(), subsubtask]

        layout = DefaultLayout(self.dossier, self.request, PDFBuilder())
        view = getMultiAdapter((self.dossier, self.request, layout), ILaTeXView)

        subtask_row = view.get_row_for_item(self.subtask.get_sql_object())
        subsubtask_row = view.get_row_for_item(subsubtask.get_sql_object())
        self.assertIn(self.task.Title(), subtask_row)
        self.assertIn(self.task.Title(), subsubtask_row)
        self.assertNotIn(self.subtask.Title(), subsubtask_row)

    def test_task_listing_latex_view_includes_subtasks(self):
        self.login(self.regular_user)
        subsubtask = create(Builder('task')
                            .titled(u'My Subsubtask')
                            .having(issuer=self.dossier_responsible.id,
                                    responsible=self.regular_user.id,
                                    responsible_client='fa',
                                    task_type='information')
                            .within(self.subtask))
        another_subtask = create(Builder('task')
                                 .titled(u'Another subtask')
                                 .having(issuer=self.dossier_responsible.id,
                                         responsible=self.regular_user.id,
                                         responsible_client='fa',
                                         task_type='information')
                                 .within(self.task))
        provide_request_layer(self.request, ITaskListingLayer)
        self.request.form['tasks'] = [self.task.absolute_url()]
        self.request.form['include_subtasks'] = 'true'

        layout = DefaultLayout(self.dossier, self.request, PDFBuilder())
        view = getMultiAdapter((self.dossier, self.request, layout), ILaTeXView)

        task_row = view.get_row_for_item(self.task.get_sql_object())
        subtask_row = view.get_row_for_item(self.subtask.get_sql_object())
        subsubtask_row = view.get_row_for_item(subsubtask.get_sql_object())
        another_subtask_row = view.get_row_for_item(another_subtask.get_sql_object())

        self.assertEqual([task_row, another_subtask_row, subtask_row,
                          subsubtask_row], view.get_rows())


class TestJournalListings(BaseLatexListingTest):

    sample_journal_entries = [
        {'action': {'visible': True,
                    'type': 'Dossier added',
                    'title': u'label_dossier_added'},
         'comments': '',
         'actor': 'peter.mueller',
         'time': DateTime(2016, 4, 12, 10, 7)},
        {'action': {'visible': True,
                    'type': 'Document added',
                    'title': u'label_document_added'},
         'comments': '',
         'actor': 'hugo.boss',
         'time': DateTime(2016, 4, 12, 12, 10)},
        {'action': {'visible': False,
                    'type': 'Dossier modified',
                    'title': u'label_dossier_modified'},
         'comments': '',
         'actor': 'peter.mueller',
         'time': DateTime(2016, 4, 25, 10, 0)},
        {'action': {'visible': False,
                    'type': 'Dossier modified',
                    'title': u'label_dossier_modified'},
         'comments': 'Lorem ipsum',
         'actor': 'peter.mueller',
         'time': DateTime(2016, 4, 25, 10, 0)},

        {'action': {'visible': True,
                    'type': 'Document Sent',
                    'title': u'label_document_sent'},
         'actor': 'test_user_1_',
         'comments': 'Attachments: sample ...',
         'time': DateTime('2016/04/12 11:35:00 GMT+2')}
    ]

    def setUp(self):
        super(TestJournalListings, self).setUp()
        dossier = create(Builder('dossier'))

        self.listing = getMultiAdapter(
            (dossier, dossier.REQUEST, self),
            ILaTexListing, name='journal')
        self.listing.items = self.sample_journal_entries

        create(Builder('ogds_user').having(userid=u'peter.mueller',
                                           firstname=u'Peter',
                                           lastname=u'M\xfcller'))
        create(Builder('ogds_user').having(userid=u'hugo.boss',
                                           firstname=u'Hugo',
                                           lastname=u'B\xf6ss'))

    def test_labels_are_translated_and_show_as_table_headers(self):
        table = lxml.html.fromstring(self.listing.template())
        cols = table.xpath(CSSSelector('thead th').path)

        self.assertEquals(
            ['Time', 'Dossier', 'Title', 'Changed by', 'Comments'],
            [col.text_content().strip() for col in cols])

    def test_shows_label_including_prinicpal_of_actor(self):
        table = lxml.html.fromstring(self.listing.template())
        rows = table.xpath(CSSSelector('tbody tr').path)

        self.assertEquals(u'M\xfcller Peter (peter.mueller)',
                          rows[0].xpath(CSSSelector('td').path)[3].text)
        self.assertEquals(u'B\xf6ss Hugo (hugo.boss)',
                          rows[1].xpath(CSSSelector('td').path)[3].text)

    def test_time_is_readable(self):
        table = lxml.html.fromstring(self.listing.template())
        rows = table.xpath(CSSSelector('tbody tr').path)

        self.assertEquals('12.04.2016 10:07',
                          rows[0].xpath(CSSSelector('td').path)[0].text)
        self.assertEquals('12.04.2016 12:10',
                          rows[1].xpath(CSSSelector('td').path)[0].text)

    def test_comment_is_included(self):
        table = lxml.html.fromstring(self.listing.template())
        rows = table.xpath(CSSSelector('tbody tr').path)

        self.assertEquals('Lorem ipsum',
                          rows[3].xpath(CSSSelector('td').path)[4].text)

    def test_document_sent_comments_are_skipped(self):
        table = lxml.html.fromstring(self.listing.template())
        rows = table.xpath(CSSSelector('tbody tr').path)

        document_sent_row = rows[4]
        self.assertEquals(
            'label_document_sent',
            document_sent_row.xpath(CSSSelector('td').path)[2].text)
        self.assertIsNone(
            document_sent_row.xpath(CSSSelector('td').path)[4].text)
