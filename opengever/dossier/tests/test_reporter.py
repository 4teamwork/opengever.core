from datetime import datetime
from ftw.testing import MockTestCase
from ftw.testing.layer import ComponentRegistryLayer
from grokcore.component.testing import grok
from mocker import ANY
from opengever.base.reporter import readable_author
from opengever.dossier.browser.report import DossierReporter
from opengever.dossier.browser.report import filing_no_number
from opengever.dossier.browser.report import filing_no_year
from opengever.dossier.browser.report import filing_no_filing
from zope.annotation.interfaces import IAttributeAnnotatable
import xlrd


class ZCMLLayer(ComponentRegistryLayer):

    def setUp(self):
        super(ZCMLLayer, self).setUp()

        import zope.security
        self.load_zcml_file('meta.zcml', zope.security)

        import Products.statusmessages
        self.load_zcml_file('configure.zcml', Products.statusmessages)


ZCML_LAYER = ZCMLLayer()


class TestDossierReporter(MockTestCase):

    layer = ZCML_LAYER

    def setUp(self):

        grok('opengever.dossier.browser.report')

    def test_filing_no_year(self):
        self.assertEquals(
            filing_no_year('OG-Leitung-2012-1'), 2012)
        self.assertEquals(
            filing_no_year('Leitung'), None)
        self.assertEquals(
            filing_no_year('OG-Direktion-2011-555'), 2011)
        self.assertEquals(
            filing_no_year(None), None)

    def test_filing_no_number(self):
        self.assertEquals(
            filing_no_number('OG-Leitung-2012-1'), 1)
        self.assertEquals(
            filing_no_number('Leitung'), None)
        self.assertEquals(
            filing_no_number('OG-Direktion-2011-555'), 555)
        self.assertEquals(
            filing_no_number(None), None)

    def test_filing_no_filing(self):
        self.assertEquals(
            filing_no_filing('OG-Leitung-2012-1'), 'Leitung')
        self.assertEquals(
            filing_no_filing('Leitung'), 'Leitung')
        self.assertEquals(
            filing_no_filing('OG-Direktion-2011-555'), 'Direktion')
        self.assertEquals(
            filing_no_filing(None), None)

    def test_get_selected_dossiers(self):
        context = self.stub()
        request = self.stub_request()
        catalog = self.stub()

        self.expect(request.get('paths')).result(
            ['dossier2',
             'dossier55',
             'dossier1',
             ])

        self.mock_tool(catalog, 'portal_catalog')

        self.expect(catalog(path={'query': 'dossier2',
                      'depth': 0})).result(['brain_2'])
        self.expect(catalog(path={'query': 'dossier55',
                      'depth': 0})).result(['brain_55'])
        self.expect(catalog(path={'query': 'dossier1',
                      'depth': 0})).result(['brain_1'])
        self.replay()

        self.assertEquals(
            DossierReporter(
                context, request).get_selected_dossiers(),
            ['brain_2', 'brain_55', 'brain_1'])

    def test_report_without_paths(self):
        context = self.providing_stub([IAttributeAnnotatable])
        request = self.stub_request(interfaces=IAttributeAnnotatable,
                                    stub_response=False)
        response = self.stub_response(request=request)

        self.expect(request.get('orig_template', ANY)).result('TEST_URL')
        self.expect(context.absolute_url()).result('TEST_URL')
        self.expect(request.get('paths')).result(None)
        self.expect(request.cookies).result({})
        self.expect(request.response.setCookie(
                'statusmessages', ANY, path=ANY)).result(None)
        self.expect(response.redirect(ANY)).result('redirected')

        self.replay()

        self.assertEquals(
            DossierReporter(context, request)(), 'redirected')

    def test_report(self):
        context = self.providing_stub([IAttributeAnnotatable])
        request = self.stub_request(interfaces=IAttributeAnnotatable,
                                    stub_response=False)
        response = self.stub_response(request=request)

        author_helper = self.mocker.replace(readable_author)
        self.expect(author_helper('Foo Hugo')).result('Readable Foo Hugo')
        self.expect(author_helper('Bar Hugo')).result('Readable Bar Hugo')

        # dossier 1
        dossier1 = self.stub()
        self.expect(dossier1.Title).result('f\xc3\xb6\xc3\xb6 dossier')
        self.expect(dossier1.start).result(datetime(2012, 1, 1))
        self.expect(dossier1.end).result(datetime(2012, 12, 1))
        self.expect(dossier1.responsible).result('Foo Hugo')
        self.expect(dossier1.filing_no).result('OG-Leitung-2012-1')
        self.expect(dossier1.review_state).result('active')
        self.expect(dossier1.reference).result('OG 3.1 / 4')

        #dossier 2
        dossier2 = self.stub()
        self.expect(dossier2.Title).result('Foo Dossier')
        self.expect(dossier2.start).result(datetime(2012, 1, 1))
        self.expect(dossier2.end).result(datetime(2012, 12, 1))
        self.expect(dossier2.responsible).result('Bar Hugo')
        self.expect(dossier2.filing_no).result('OG-Leitung-2012-1')
        self.expect(dossier2.review_state).result('active')
        self.expect(dossier2.reference).result('OG 3.1 / 5')

        # fake
        self.expect(request.get('paths')).result(['path1', 'path2'])

        view = self.mocker.patch(DossierReporter(context, request))
        self.expect(view.get_selected_dossiers()).result(
            [dossier1, dossier2])

        self.expect(response.setHeader(
                'Content-Type', 'application/vnd.ms-excel'))
        self.expect(response.setHeader('Content-Disposition',
                               'attachment;filename="dossier_report.xls"'))

        self.replay()

        data = view()
        self.assertTrue(len(data) > 0)

        wb = xlrd.open_workbook(file_contents=data)
        sheet = wb.sheets()[0]
        row1 = sheet.row(1)
        self.assertEquals(
            [cell.value for cell in row1],
            [u'f\xf6\xf6 dossier',
             u'01.01.2012',
             u'01.12.2012',
             u'Readable Foo Hugo',
             u'Leitung',
             2012.0,
             1.0,
             u'OG-Leitung-2012-1',
             u'active',
             u'OG 3.1 / 4']
            )
