from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from lxml.cssselect import CSSSelector
from opengever.latex.listing import ILaTexListing
from opengever.testing import FunctionalTestCase
from opengever.testing import create_and_select_current_org_unit
from opengever.testing import create_ogds_user
from opengever.testing import obj2brain
from zope.component import getMultiAdapter
import lxml


class TestDossierListing(FunctionalTestCase):

    def setUp(self):
        super(TestDossierListing, self).setUp()

        create_and_select_current_org_unit('client1')
        create_ogds_user('hugo.boss')

        self.repo = create(Builder('repository').titled('Repository XY'))
        self.dossier = create(Builder('dossier')
                          .within(self.repo)
                          .having(title=u'Dossier A',
                                  responsible="hugo.boss",
                                  start=date(2013, 11, 1),
                                  end=date(2013, 12, 31))
                          .in_state('dossier-state-resolved'))
        self.subdossier = create(Builder('dossier')
                                 .within(self.dossier)
                          .having(title=u'Dossier B',
                                  start=date(2013, 11, 1),
                                  responsible="hugo.boss"))

        self.listing = getMultiAdapter(
            (self.repo, self.repo.REQUEST, self),
            ILaTexListing, name='dossiers')

    def test_get_responsible_returns_client_title_and_user_description(self):

        responsible = self.listing.get_responsible(
            obj2brain(self.dossier))

        self.assertEquals(u'Client1 / Boss Hugo (hugo.boss)', responsible)

    def test_get_repository_title_returns_the_title_of_the_first_parental_repository_folder(self):

        self.assertEquals(
            '1. Repository XY',
            self.listing.get_repository_title(obj2brain(self.dossier)))

        self.assertEquals(
            '1. Repository XY',
            self.listing.get_repository_title(
                obj2brain(self.subdossier)))

    def test_configured_width_is_set_in_the_colgroup(self):
        self.listing.brains = [obj2brain(self.dossier),
                               obj2brain(self.subdossier)]

        table = lxml.html.fromstring(self.listing.template())
        cols = table.xpath(CSSSelector('col').path)

        self.assertEquals(
            ['10%', '5%', '20%', '25%', '20%', '10%', '5%', '5%'],
            [col.get('width') for col in cols])

    def test_labels_are_translated_and_show_as_table_headers(self):
        self.listing.brains = [obj2brain(self.dossier),
                               obj2brain(self.subdossier)]

        table = lxml.html.fromstring(self.listing.template())
        cols = table.xpath(CSSSelector('thead th').path)

        self.assertEquals(
            ['Reference number', 'No.', 'Repositoryfolder', 'Title',
             'Responsible', 'State', 'Start', 'End'],
            [col.text_content().strip() for col in cols])

    def test_full_values_rendering(self):
        self.listing.brains = [obj2brain(self.dossier),
                               obj2brain(self.subdossier)]

        table = lxml.html.fromstring(self.listing.template())
        rows = table.xpath(CSSSelector('tbody tr').path)

        self.assertEquals(
            ['OG 1 / 1',
             '1',
             '1. Repository XY',
             'Dossier A',
             'Client1 / Boss Hugo (hugo.boss)',
             'dossier-state-resolved',
             '01.11.2013',
             '31.12.2013'],
            [value.text_content().strip() for value in rows[0].xpath(CSSSelector('td').path)])

        self.assertEquals(
            ['OG 1 / 1.1',
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

        create_and_select_current_org_unit('client1')
        create_ogds_user('hugo.boss')

        self.repo = create(Builder('repository').titled('Repository XY'))
        self.dossier = create(Builder('dossier')
                          .within(self.repo)
                          .having(title=u'Dossier A',
                                  responsible="hugo.boss",
                                  start=date(2013, 11, 1),
                                  end=date(2013, 12, 31))
                          .in_state('dossier-state-resolved'))

        self.listing = getMultiAdapter(
            (self.repo, self.repo.REQUEST, self),
            ILaTexListing, name='subdossiers')

    def test_labels_are_translated_and_show_as_table_headers(self):
        self.listing.brains = [obj2brain(self.dossier)]

        table = lxml.html.fromstring(self.listing.template())
        cols = table.xpath(CSSSelector('thead th').path)

        self.assertEquals(
            ['No.', 'Title', 'Responsible', 'State', 'Start', 'End'],
            [col.text_content().strip() for col in cols])

    def test_drop_reference_from_default_dossier_listings(self):
        self.listing.brains = [obj2brain(self.dossier)]

        table = lxml.html.fromstring(self.listing.template())
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

        create_and_select_current_org_unit('client1')

        self.document = create(Builder('document')
                               .having(title=u'Document A',
                                       document_date=date(2013, 11, 4),
                                       receipt_date=date(2013, 11, 6),
                                       document_author='Hugo Boss'))

        self.listing = getMultiAdapter(
            (self.document, self.document.REQUEST, self),
            ILaTexListing, name='documents')

    def test_drop_reference_and_sequence_number_from_default_dossier_listings(self):
        self.listing.brains = [obj2brain(self.document)]

        table = lxml.html.fromstring(self.listing.template())
        rows = table.xpath(CSSSelector('tbody tr').path)

        self.assertEquals(
            ['1',
             'Document A',
             '04.11.2013',
             '06.11.2013',
             '',
             'Hugo Boss'],
            [value.text_content().strip() for value in rows[0].xpath(CSSSelector('td').path)])


class TestTaskLisitings(FunctionalTestCase):

    def setUp(self):
        super(TestTaskLisitings, self).setUp()

        create_and_select_current_org_unit('client1')
        create_ogds_user('hugo.boss')

        self.task = create(Builder('task')
                           .having(
                               title='Task A',
                               task_type='approval',
                               responsible='hugo.boss',
                               responsible_client='client1',
                               issuer='hugo.boss',
                               deadline=date(2013, 11, 6))
                           .in_state('task-state-in-progress'))

        self.listing = getMultiAdapter(
            (self.task, self.task.REQUEST, self),
            ILaTexListing, name='tasks')

    def test_labels_are_translated_and_show_as_table_headers(self):
        self.listing.brains = [obj2brain(self.task), obj2brain(self.task)]

        table = lxml.html.fromstring(self.listing.template())
        cols = table.xpath(CSSSelector('thead th').path)

        self.assertEquals(
            ['No.', 'Task type', 'Issuer', 'Responsible', 'State', 'Title', 'Deadline'],
            [col.text_content().strip() for col in cols])

    def test_drop_reference_and_sequence_number_from_default_dossier_listings(self):
        self.listing.brains = [obj2brain(self.task)]

        table = lxml.html.fromstring(self.listing.template())
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
