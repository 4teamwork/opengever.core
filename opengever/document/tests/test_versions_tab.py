from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.testing import FunctionalTestCase
from plone import api
from urlparse import parse_qs
from urlparse import urlparse
import transaction


class TestVersionsTab(FunctionalTestCase):

    def setUp(self):
        super(TestVersionsTab, self).setUp()
        lang_tool = api.portal.get_tool('portal_languages')
        lang_tool.addSupportedLanguage('de-ch')
        lang_tool.setDefaultLanguage('de-ch')

        self.dossier = create(Builder('dossier')
                              .titled(u'Testdossier'))
        self.document = self._create_doc_with_versions()
        transaction.commit()

        self.test_user = create(Builder('ogds_user')
                                .id('test-user')
                                .having(firstname=u'Hugo', lastname=u'Boss'))

    def _create_doc_with_versions(self, n=3):
        doc = self._create_doc()
        for version_id in range(1, n + 1):
            self._create_version(doc, version_id)
        return doc

    def _create_doc(self):
        doc = create(Builder('document')
                     .within(self.dossier)
                     .attach_file_containing(u"INITIAL VERSION DATA",
                                             u"somefile.txt"))
        return doc

    def _create_version(self, doc, version_id):
        repo = api.portal.get_tool('portal_repository')
        vdata = 'VERSION {} DATA'.format(version_id)
        doc.file.data = vdata
        repo.save(obj=doc, comment="This is Version %s" % version_id)


class TestVersionsTabWithoutPDFConverter(TestVersionsTab):

    @browsing
    def test_dates_are_formatted_correctly(self, browser):
        with freeze(datetime(2015, 01, 28, 12, 00)):
            doc = self._create_doc()
        with freeze(datetime(2015, 01, 28, 18, 30)):
            self._create_version(doc, 1)
        transaction.commit()

        browser.login().open(doc, view='tabbedview_view-versions')
        listing = browser.css('.listing').first
        dates = [d['Datum']for d in listing.dicts()]
        self.assertEquals(['28.01.2015 18:30', '28.01.2015 12:00'], dates)

    @browsing
    def test_is_sorted_by_descending_version_id(self, browser):
        browser.login().open(self.document, view='tabbedview_view-versions')
        listing = browser.css('.listing').first
        version_ids = [d['Version'] for d in listing.dicts()]
        self.assertEquals(['3', '2', '1', '0'], version_ids)

    @browsing
    def test_columns_are_ordered_and_translated(self, browser):
        browser.login().open(self.document, view='tabbedview_view-versions')
        listing = browser.css('.listing').first
        column_headers = listing.lists()[0]
        self.assertEquals(
            ['Version', u'Ge\xe4ndert von', 'Datum', 'Kommentar', '', ''],
            column_headers)

    @browsing
    def test_actor_is_linked(self, browser):
        browser.login().open(self.document, view='tabbedview_view-versions')
        listing = browser.css('.listing').first
        first_row = listing.css('tr')[1]
        actor_link = first_row.css('td a').first

        self.assertEquals('Boss Hugo (test-user)', actor_link.text)
        self.assertEquals('http://nohost/plone/@@user-details/test-user',
                          actor_link.attrib['href'])

    @browsing
    def test_revert_link_is_properly_constructed(self, browser):
        browser.login().open(self.document, view='tabbedview_view-versions')
        listing = browser.css('.listing').first
        first_row = listing.css('tr')[1]
        revert_link = first_row.css('td a')[-1]
        url = urlparse(revert_link.attrib['href'])
        query = parse_qs(url.query)

        self.assertEquals(u'Zur\xfccksetzen', revert_link.text)
        self.assertEquals(['3'], query['version_id'])
        self.assertIn('_authenticator', query)
        self.assertEquals(
            '/plone/dossier-1/document-1/revert-file-to-version', url.path)

    @browsing
    def test_download_link_is_properly_constructed(self, browser):
        browser.login().open(self.document, view='tabbedview_view-versions')
        listing = browser.css('.listing').first
        first_row = listing.css('tr')[1]
        download_link = first_row.css('td a')[-2]
        url = urlparse(download_link.attrib['href'])
        query = parse_qs(url.query)

        self.assertEquals('Kopie herunterladen', download_link.text)
        self.assertEquals(['3'], query['version_id'])
        self.assertIn('_authenticator', query)
        self.assertEquals(
            '/plone/dossier-1/document-1/file_download_confirmation', url.path)


class TestVersionsTabWithPDFConverter(TestVersionsTab):

    def setUp(self):
        super(TestVersionsTabWithPDFConverter, self).setUp()
        import opengever.document
        opengever.document.browser.versions_tab.PDFCONVERTER_AVAILABLE = True

    def tearDown(self):
        super(TestVersionsTabWithPDFConverter, self).tearDown()
        import opengever.document
        opengever.document.browser.versions_tab.PDFCONVERTER_AVAILABLE = False

    @browsing
    def test_download_pdf_link_is_properly_constructed(self, browser):
        browser.login().open(self.document, view='tabbedview_view-versions')

        listing = browser.css('.listing').first
        first_row = listing.css('tr')[1]
        pdf_download_link = first_row.css('td a')[-2]
        url = urlparse(pdf_download_link.attrib['href'])
        query = parse_qs(url.query)

        self.assertEquals('PDF Vorschau', pdf_download_link.text)
        self.assertEquals(['3'], query['version_id'])
        self.assertIn('_authenticator', query)
        self.assertEquals(
            '/plone/dossier-1/document-1/download_pdf_version', url.path)
