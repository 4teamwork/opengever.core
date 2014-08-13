from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from lxml.cssselect import CSSSelector
from opengever.latex.listing import DocumentsLaTeXListing
from opengever.latex.listing import DossiersLaTeXListing
from opengever.latex.listing import SubDossiersLaTeXListing
from opengever.latex.listing import TasksLaTeXListing
from opengever.testing import FunctionalTestCase
from opengever.testing import obj2brain
import lxml


class TestDossierListing(FunctionalTestCase):

    def setUp(self):
        super(TestDossierListing, self).setUp()

        self.hugo = create(Builder('fixture').with_hugo_boss())

        self.repo = create(Builder('repository').titled('Repository XY'))
        self.dossier = create(Builder('dossier')
                          .within(self.repo)
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

    def get_listing(self, items=[]):
        return DossiersLaTeXListing(self, items)

    def test_get_responsible_returns_client_title_and_user_description(self):

        responsible = self.get_listing().get_responsible(
            obj2brain(self.dossier))

        self.assertEquals(u'Client1 / Boss Hugo (hugo.boss)', responsible)

    def test_get_repository_title_returns_the_title_of_the_first_parental_repository_folder(self):
        listing = self.get_listing()
        self.assertEquals(
            '1. Repository XY',
            listing.get_repository_title(obj2brain(self.dossier)))

        self.assertEquals(
            '1. Repository XY',
            listing.get_repository_title(obj2brain(self.subdossier)))

    def test_configured_width_is_set_in_the_colgroup(self):
        listing = self.get_listing([obj2brain(self.dossier),
                                    obj2brain(self.subdossier)])

        table = lxml.html.fromstring(listing.template())
        cols = table.xpath(CSSSelector('col').path)

        self.assertEquals(
            ['10%', '5%', '20%', '25%', '20%', '10%', '5%', '5%'],
            [col.get('width') for col in cols])

    def test_labels_are_translated_and_show_as_table_headers(self):
        listing = self.get_listing([obj2brain(self.dossier),
                                    obj2brain(self.subdossier)])

        table = lxml.html.fromstring(listing.template())
        cols = table.xpath(CSSSelector('thead th').path)

        self.assertEquals(
            ['Reference number', 'No.', 'Repositoryfolder', 'Title',
             'Responsible', 'State', 'Start', 'End'],
            [col.text_content().strip() for col in cols])

    def test_full_values_rendering(self):
        listing = self.get_listing([obj2brain(self.dossier),
                                    obj2brain(self.subdossier)])

        table = lxml.html.fromstring(listing.template())
        rows = table.xpath(CSSSelector('tbody tr').path)

        self.assertEquals(
            ['Client1 1 / 1',
             '1',
             '1. Repository XY',
             'Dossier A',
             'Client1 / Boss Hugo (hugo.boss)',
             'dossier-state-resolved',
             '01.11.2013',
             '31.12.2013'],
            [value.text_content().strip() for value in rows[0].xpath(CSSSelector('td').path)])

        self.assertEquals(
            ['Client1 1 / 1.1',
             '2',
             '1. Repository XY',
             'Dossier B',
             'Client1 / Boss Hugo (hugo.boss)',
             'dossier-state-active',
             '01.11.2013',
             ''],
            [value.text_content().strip() for value in rows[1].xpath(CSSSelector('td').path)])


class TestSubDossierListing(FunctionalTestCase):

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

    def get_listing(self, items=[]):
        return SubDossiersLaTeXListing(self, items)

    def test_labels_are_translated_and_show_as_table_headers(self):
        listing = self.get_listing([obj2brain(self.dossier)])

        table = lxml.html.fromstring(listing.template())
        cols = table.xpath(CSSSelector('thead th').path)

        self.assertEquals(
            ['No.', 'Title', 'Responsible', 'State', 'Start', 'End'],
            [col.text_content().strip() for col in cols])

    def test_drop_reference_from_default_dossier_listings(self):
        listing = self.get_listing([obj2brain(self.dossier)])

        table = lxml.html.fromstring(listing.template())
        rows = table.xpath(CSSSelector('tbody tr').path)

        self.assertEquals(
            ['1',
             'Dossier A',
             'Client1 / Boss Hugo (hugo.boss)',
             'dossier-state-resolved',
             '01.11.2013',
             '31.12.2013'],
            [value.text_content().strip() for value in rows[0].xpath(CSSSelector('td').path)])


class TestDocumentListing(FunctionalTestCase):

    def setUp(self):
        super(TestDocumentListing, self).setUp()

        self.document = create(Builder('document')
                               .having(title=u'Document A',
                                       document_date=date(2013, 11, 4),
                                       receipt_date=date(2013, 11, 6),
                                       document_author='Hugo Boss'))

    def get_listing(self, items=[]):
        return DocumentsLaTeXListing(self, items)

    def test_drop_reference_and_sequence_number_from_default_dossier_listings(self):
        listing = self.get_listing([obj2brain(self.document)])

        table = lxml.html.fromstring(listing.template())
        rows = table.xpath(CSSSelector('tbody tr').path)

        self.assertEquals(
            ['1',
             'Document A',
             '04.11.2013',
             '06.11.2013',
             '',
             'Hugo Boss'],
            [value.text_content().strip() for value in rows[0].xpath(CSSSelector('td').path)])


class TestTaskListings(FunctionalTestCase):

    def setUp(self):
        super(TestTaskListings, self).setUp()

        self.hugo = create(Builder('fixture').with_hugo_boss())

        self.org_unit_2 = create(Builder('org_unit').id('client2'))

        self.task = create(Builder('task')
                           .having(
                               title='Task A',
                               task_type='approval',
                               responsible=self.hugo.userid,
                               responsible_client=self.org_unit.id(),
                               issuer=self.hugo.userid,
                               deadline=date(2013, 11, 6))
                           .in_state('task-state-in-progress'))

    def get_listing(self, items=[]):
        return TasksLaTeXListing(self, items)

    def test_labels_are_translated_and_show_as_table_headers(self):
        listing = self.get_listing([self.task.get_sql_object(),
                                    self.task.get_sql_object()])

        table = lxml.html.fromstring(listing.template())
        cols = table.xpath(CSSSelector('thead th').path)

        self.assertEquals(
            ['No.', 'Task type', 'Issuer', 'Responsible', 'State', 'Title', 'Deadline'],
            [col.text_content().strip() for col in cols])

    def test_drop_reference_and_sequence_number_from_default_task_listings(self):
        listing = self.get_listing([self.task.get_sql_object()])

        table = lxml.html.fromstring(listing.template())
        rows = table.xpath(CSSSelector('tbody tr').path)

        self.assertEquals(
            ['1',
             'For approval',
             'Client1 / Boss Hugo',
             'Client1 / Boss Hugo',
             'task-state-in-progress',
             'Task A',
             '06.11.2013'],
            [value.text_content().strip() for value in rows[0].xpath(CSSSelector('td').path)])

    @browsing
    def test_task_listing(self, browser):
        task_id = self.task.get_sql_object().id
        browser.login().open(data={'pdf-tasks-listing:method': 1,
                                   'task_ids:list': task_id})
