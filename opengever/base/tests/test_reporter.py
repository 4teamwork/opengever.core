from datetime import datetime, timedelta
from ftw.testing import MockTestCase
from mocker import ANY
from opengever.base import _
from zope.i18n.tests.test_itranslationdomain import Environment
from opengever.base.reporter import ReportingController, XLSReporter
from opengever.base.reporter import StringTranslater
from opengever.base.reporter import format_datetime, get_date_style
from opengever.base.reporter import readable_author
from opengever.ogds.base.interfaces import IContactInformation
import xlrd


class TestReportingController(MockTestCase):

    def test_controller(self):
        context = self.mocker.mock()
        request = self.mocker.mock()

        contact_info = self.stub()
        self.mock_utility(contact_info, IContactInformation, name=u"")
        with self.mocker.order():
            self.expect(contact_info.is_user_in_inbox_group()).result(
                False)
            self.expect(contact_info.is_user_in_inbox_group()).result(
                True)

        self.replay()

        self.assertFalse(ReportingController(context, request).render())
        self.assertTrue(ReportingController(context, request).render())

    def test_xlsreporter(self):
        contact_info = self.stub()
        self.mock_utility(contact_info, IContactInformation, name=u"")
        self.expect(contact_info.is_user(ANY)).result(True)
        self.expect(
            contact_info.describe(ANY)).result('Describe text for a user')

        request = self.mocker.mock()
        brains = []

        for i in range(2):
            brain = self.stub()
            self.expect(brain.Title).result('Objekt %i' % (i))
            self.expect(brain.start).result(
                datetime(2012, 2, 25) + timedelta(i))
            self.expect(brain.responsible).result('Test user %i' % (i))
            self.expect(brain.review_state).result('dossier-state-activ')
            brains.append(brain)

        self.replay()

        translation_request = Environment(('de', 'de'))

        test_attributes = [
            {'id':'Title', 'title':_('label_title', default='Title')},
            {'id':'start', 'title':_('label_start', default='Start'),
             'transform': format_datetime, 'style':get_date_style()},
            {'id':'responsible',
             'title':_('label_responsible', default='Responsible'),
             'transform':readable_author},
            {'id':'review_state',
             'title':_('label_review_state', default='Review state'),
             'transform':StringTranslater(
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
            [u'Title', u'Start', u'Responsible', u'Review state'])

        row1 = sheet.row(1)
        self.assertEquals(
            [cell.value for cell in row1],
            [u'Objekt 0', u'25.02.2012', u'Describe text for a user',
             u'dossier-state-activ'])

        row2 = sheet.row(2)
        self.assertEquals(
            [cell.value for cell in row2],
            [u'Objekt 1', u'26.02.2012', u'Describe text for a user',
             u'dossier-state-activ'])
