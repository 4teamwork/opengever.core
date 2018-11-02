from datetime import datetime
from DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.document.versioner import Versioner
from opengever.testing import FunctionalTestCase
from opengever.testing.helpers import create_document_version
from plone import api
from urlparse import parse_qs
from urlparse import urlparse
import transaction


class BaseVersionsTab(FunctionalTestCase):

    def setUp(self):
        super(BaseVersionsTab, self).setUp()
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
            create_document_version(doc, version_id,
                                    comment=u'Kommentar mit Uml\xe4ut')
        return doc

    def _create_doc(self):
        doc = create(Builder('document')
                     .within(self.dossier)
                     .attach_file_containing(u"INITIAL VERSION DATA",
                                             u"somefile.txt"))

        Versioner(doc).create_initial_version()

        return doc


class TestVersionsTab(BaseVersionsTab):

    @browsing
    def test_dates_are_formatted_correctly(self, browser):
        with freeze(datetime(2015, 01, 28, 12, 00)):
            doc = self._create_doc()
        with freeze(datetime(2015, 01, 28, 18, 30)):
            create_document_version(doc, 1)
        transaction.commit()

        browser.login().open(doc, view='tabbedview_view-versions')
        listing = browser.css('.listing').first
        dates = [d['Datum']for d in listing.dicts()]
        self.assertEquals(['28.01.2015 18:30', '28.01.2015 12:00'], dates)

    @browsing
    def test_handles_version_comments_that_are_none(self, browser):
        doc = self._create_doc()

        repository = api.portal.get_tool('portal_repository')
        repository.save(obj=doc, comment=None)
        transaction.commit()

        browser.login().open(doc, view='tabbedview_view-versions')
        listing = browser.css('.listing').first
        comments = [d['Kommentar'] for d in listing.dicts()]
        self.assertEquals(
            ['', 'Dokument erstellt (Initialversion)'], comments)

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
            ['Version',
             u'Ge\xe4ndert von',
             'Datum',
             'Kommentar',
             'Kopie herunterladen',
             u'Zur\xfccksetzen'],
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
    def test_lists_original_creator_as_actor_for_initial_version(self, browser):
        create(Builder('ogds_user')
               .id('original-document-creator')
               .having(firstname=u'Firstname', lastname=u'Lastname'))
        self.document.creators = ('original-document-creator', )
        transaction.commit()

        browser.login().open(self.document, view='tabbedview_view-versions')
        listing = browser.css('.listing').first
        last_row = listing.css('tr')[-1]
        actor_link = last_row.css('td a').first

        self.assertEquals(
            'Lastname Firstname (original-document-creator)', actor_link.text)

    @browsing
    def test_revert_link_is_properly_constructed(self, browser):
        browser.login().open(self.document,
                             view='tabbedview_view-versions')
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
        browser.login().open(self.document,
                             view='tabbedview_view-versions')
        listing = browser.css('.listing').first
        first_row = listing.css('tr')[1]
        download_link = first_row.css('td a')[-2]
        url = urlparse(download_link.attrib['href'])
        query = parse_qs(url.query)

        self.assertEquals('Kopie herunterladen', download_link.text)
        self.assertEquals(['3'], query['version_id'])
        self.assertIn('_authenticator', query)
        self.assertEquals(
            '/plone/dossier-1/document-1/file_download_confirmation',
            url.path)


class TestVersionsTabWithBubmelbeeActivated(BaseVersionsTab):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    @browsing
    def test_columns_are_ordered_and_translated(self, browser):
        browser.login().open(self.document, view='tabbedview_view-versions')
        listing = browser.css('.listing').first
        column_headers = listing.lists()[0]
        self.assertEquals(
            ['Version',
             u'Ge\xe4ndert von',
             'Datum',
             'Kommentar',
             'Kopie herunterladen',
             u'Zur\xfccksetzen',
             'Vorschau',
             'PDF speichern unter'],
            column_headers)

    @browsing
    def test_preview_link_is_properly_constructed(self, browser):
        browser.login().open(self.document, view='tabbedview_view-versions')

        preview_link = browser.css('.listing .showroom-item').first

        self.assertEquals('Vorschau', preview_link.text)
        self.assertIn(
            '/plone/dossier-1/document-1/@@bumblebee-overlay-listing?version_id=3',
            preview_link.attrib['href'])


class TestVersionsTabForDocumentWithoutInitialVersion(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    def setUp(self):
        super(TestVersionsTabForDocumentWithoutInitialVersion, self).setUp()

        self.dossier = create(Builder('dossier').titled(u'Testdossier'))
        self.document = create(Builder('document')
                               .with_creation_date(DateTime(2016, 11, 6))
                               .with_dummy_content())

    @browsing
    def test_list_initial_version_even_if_it_does_not_exists(self, browser):
        browser.login().open(self.document, view='tabbedview_view-versions')

        listing = browser.css('.listing').first
        self.assertEquals(
            [{'Comment': 'Initial version',
              'Download copy': 'Download copy',
              'Preview': 'Preview',
              'Revert': '',
              'Save PDF': 'Save PDF',
              'Version': '0',
              'Date': 'Nov 06, 2016 12:00 AM',
              'Changed by': 'Test User (test_user_1_)'}],
            listing.dicts())

    @browsing
    def test_shows_custom_initial_comment_when_set(self, browser):
        Versioner(self.document).set_custom_initial_version_comment(
            u'Document copied from task (task closed)')
        transaction.commit()

        browser.login().open(self.document, view='tabbedview_view-versions')

        listing = browser.css('.listing').first
        self.assertEquals(
            u'Document copied from task (task closed)',
            listing.dicts()[0].get('Comment'))

    @browsing
    def test_uses_working_copy_for_bumblebee_link(self, browser):
        browser.login().open(self.document, view='tabbedview_view-versions')

        self.assertEquals(
            'http://nohost/plone/document-1/@@bumblebee-overlay-listing',
            browser.find_link_by_text('Preview').get('href'))
