from datetime import datetime, timedelta
from ftw.builder import Builder
from ftw.builder import create
from ftw.testing import MockTestCase
from Missing import Value as MissingValue
from opengever.base import _
from opengever.base.reporter import format_datetime
from opengever.base.reporter import get_date_style
from opengever.base.reporter import readable_author
from opengever.base.reporter import StringTranslater
from opengever.base.reporter import XLSReporter
from opengever.testing import MEMORY_DB_LAYER
from zope.i18n.tests.test_itranslationdomain import Environment
import xlrd


class TestReporter(MockTestCase):

    layer = MEMORY_DB_LAYER

    def test_xlsreporter(self):
        create(Builder('ogds_user').id('test_user_0'))
        create(Builder('ogds_user').id('test_user_1'))

        request = self.mocker.mock()
        brains = []

        for i in range(2):
            brain = self.stub()
            self.expect(brain.Title).result('Objekt %i' % (i))
            self.expect(brain.missing).result(MissingValue)
            self.expect(brain.start).result(
                datetime(2012, 2, 25) + timedelta(i))
            self.expect(brain.responsible).result('test_user_%i' % (i))
            self.expect(brain.review_state).result('dossier-state-active')
            brains.append(brain)

        self.replay()

        translation_request = Environment(('de', 'de'))

        test_attributes = [
            {'id': 'Title', 'title': _('label_title', default='Title')},
            #test missingvalue
            {'id': 'missing', 'missing': 'Missing', },
            {'id': 'start', 'title': _('label_start', default='Start'),
             'transform': format_datetime, 'style': get_date_style()},
            {'id': 'responsible',
             'title': _('label_responsible', default='Responsible'),
             'transform': readable_author},
            {'id': 'review_state',
             'title': _('label_review_state', default='Review state'),
             'transform': StringTranslater(
                 translation_request, 'plone').translate},
        ]

        # generate the report.xls
        reporter = XLSReporter(request, test_attributes, brains)
        data = reporter()

        # check the generate xls with the xlrd module
        wb = xlrd.open_workbook(file_contents=data)
        sheet = wb.sheets()[0]

        labels = sheet.row(0)
        self.assertEquals(
            [cell.value for cell in labels],
            [u'Title', u'', u'Start', u'Responsible', u'Review state'])

        row1 = sheet.row(1)
        self.assertEquals(
            [cell.value for cell in row1],
            [u'Objekt 0', u'', u'25.02.2012', u'test_user_0 (test_user_0)',
             u'dossier-state-active'])

        row2 = sheet.row(2)
        self.assertEquals(
            [cell.value for cell in row2],
            [u'Objekt 1', u'', u'26.02.2012', u'test_user_1 (test_user_1)',
             u'dossier-state-active'])
