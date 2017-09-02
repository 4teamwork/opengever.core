from datetime import datetime
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import MockTestCase
from Missing import Value as MissingValue
from opengever.base import _
from opengever.base.reporter import DATE_NUMBER_FORMAT
from opengever.base.reporter import readable_author
from opengever.base.reporter import StringTranslater
from opengever.base.reporter import XLSReporter
from opengever.testing import MEMORY_DB_LAYER
from openpyxl import load_workbook
from tempfile import NamedTemporaryFile
from zope.i18n.tests.test_itranslationdomain import Environment


class TestReporter(MockTestCase):

    layer = MEMORY_DB_LAYER

    def setUp(self):
        super(TestReporter, self).setUp()

        create(Builder('ogds_user').id('test_user_0'))
        create(Builder('ogds_user').id('test_user_1'))

        self.request = self.mocker.mock()
        self.brains = []
        for i in range(2):
            brain = self.stub()
            self.expect(brain.Title).result('Objekt %i' % (i))
            self.expect(brain.missing).result(MissingValue)
            self.expect(brain.start).result(
                datetime(2012, 2, 25) + timedelta(i))
            self.expect(brain.responsible).result('test_user_%i' % (i))
            self.expect(brain.review_state).result('dossier-state-active')
            self.brains.append(brain)

        self.replay()

        translation_request = Environment(('de', 'de'))

        self.test_attributes = [
            {'id': 'Title', 'title': _('label_title', default='Title')},
            {'id': 'missing', 'missing': 'Missing', },
            {'id': 'start', 'title': _('label_start', default='Start'),
             'number_format': DATE_NUMBER_FORMAT},
            {'id': 'responsible',
             'title': _('label_responsible', default='Responsible'),
             'transform': readable_author},
            {'id': 'review_state',
             'title': _('label_review_state', default='Review state'),
             'transform': StringTranslater(
                 translation_request, 'plone').translate},
        ]

    def test_label_row_is_translated_attribute_titles(self):
        reporter = XLSReporter(self.request, self.test_attributes, self.brains)
        workbook = self.get_workbook(reporter())
        self.assertEquals(
            [u'Title', None, u'Start', u'Responsible', u'Review state'],
            [cell.value for cell in list(workbook.active.rows)[0]])

    def test_value_rows(self):
        reporter = XLSReporter(self.request, self.test_attributes, self.brains)
        workbook = self.get_workbook(reporter())

        rows = list(workbook.active.rows)
        self.assertEquals(
            [u'Objekt 0', None, datetime(2012, 2, 25),
             u'test_user_0 (test_user_0)', u'dossier-state-active'],
            [cell.value for cell in rows[1]])

        self.assertEquals(
            [u'Objekt 1', None, datetime(2012, 2, 26),
             u'test_user_1 (test_user_1)', 'dossier-state-active'],
            [cell.value for cell in rows[2]])

    def test_set_sheet_title_for_active_workbook_sheet(self):
        title = 'Aufgaben\xc3\xbcbersicht'.decode('utf-8')
        reporter = XLSReporter(
            None, [], [], sheet_title=title)

        workbook = self.get_workbook(reporter())
        self.assertEquals(title, workbook.active.title)

    def get_workbook(self, data):
        with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmpfile:
            tmpfile.write(data)
            tmpfile.flush()
            workbook = load_workbook(tmpfile.name)

        return workbook
