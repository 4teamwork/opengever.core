from ftw.builder import Builder
from ftw.builder import create
from ftw.solr.connection import SolrResponse
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from lxml import etree
from opengever.base.solr import OGSolrContentListing
from opengever.base.solr import OGSolrContentListingObject
from opengever.base.solr import OGSolrDocument
from opengever.tabbedview import BaseCatalogListingTab
from opengever.testing import IntegrationTestCase
from opengever.testing import solr_data_for
from opengever.testing import SolrFunctionalTestCase
from plone import api
import os
import pkg_resources


def get_subclasses(cls):
    for subclass in cls.__subclasses__():
        yield subclass
        for subsubclass in get_subclasses(subclass):
            yield subsubclass


class TestSolr(IntegrationTestCase):

    def test_solr_schema_contains_all_tabbedview_columns(self):
        pkg_path = pkg_resources.get_distribution('opengever.core').location
        tree = etree.parse(os.path.join(pkg_path, 'solr-conf', 'managed-schema.xml'))
        solr_fields = tree.xpath('.//field/@name')
        tabs = get_subclasses(BaseCatalogListingTab)
        for tab in tabs:
            try:
                columns = [c['column'] for c in tab.columns if c['column']]
            except TypeError:
                columns = []
            for column in columns:
                self.assertIn(
                    column,
                    solr_fields,
                    'Solr schema is missing field {} used in {}.'.format(
                        column, tab))

    def test_solr_schema_contains_all_search_options_columns(self):
        pkg_path = pkg_resources.get_distribution('opengever.core').location
        tree = etree.parse(os.path.join(pkg_path, 'solr-conf', 'managed-schema.xml'))
        solr_fields = tree.xpath('.//field/@name')
        tabs = get_subclasses(BaseCatalogListingTab)
        for tab in tabs:
            columns = tab.search_options.keys()
            for column in columns:
                self.assertIn(
                    column,
                    solr_fields,
                    'Solr schema is missing field {} used in search_options '
                    'of {}.'.format(column, tab))

    def test_contentlisting_returns_og_types(self):
        body = """{
            "responseHeader": {"status": 0},
            "response": {
                "numFound": 1,
                "start": 0,
                "docs": [{
                    "UID": "85bed8c49f6d4f8b841693c6a7c6cff1",
                    "Title": "My Item"
                }]
            }
        }"""
        resp = SolrResponse(body=body, status=200)
        listing = OGSolrContentListing(resp)
        self.assertTrue(isinstance(listing[0], OGSolrContentListingObject))
        self.assertTrue(isinstance(listing[0].doc, OGSolrDocument))

    def test_solr_schema_contains_all_new_indexes_and_metadata(self):
        pkg_path = pkg_resources.get_distribution('opengever.core').location
        tree = etree.parse(os.path.join(pkg_path, 'solr-conf', 'managed-schema.xml'))
        solr_fields = tree.xpath('.//field/@name')

        catalog = api.portal.get_tool('portal_catalog')

        # indexes
        CATALOG_ONLY_INDEXES = [
            'Type',
            'after_resolve_jobs_pending',
            'blocked_local_roles',
            'cmf_uid',
            'contactid',
            'date_of_completion',
            'getId',
            'predecessor',
            'hide_member_details',
        ]

        for index in catalog.indexes():
            if index not in CATALOG_ONLY_INDEXES:
                self.assertIn(
                    index, solr_fields,
                    '`{}` is missing in the solr schema fields, or is it a '
                    'catalog only index?'.format(index))

        CATALOG_ONLY_METADATA = [
            'Type',
            'cmf_uid',
            'contactid',
            'css_icon_class',
            'date_of_completion',
            'exclude_from_nav',
            'getContentType',
            'getId',
            'in_response_to',
            'listCreators',
            'predecessor',
            'title_de',
            'title_fr',
            'title_en',
            'gever_doc_uid',
        ]

        for metadata in catalog.schema():
            if metadata not in CATALOG_ONLY_METADATA:
                self.assertIn(
                    metadata, solr_fields,
                    '`{}` is missing in the solr schema fields, or is it a '
                    'catalog only metadata?'.format(metadata))


class TestOGSolrDocument(IntegrationTestCase):

    def test_without_bumblebee_checksum(self):
        doc = OGSolrDocument(data={})
        self.assertEqual(doc.bumblebee_checksum, None)

    def test_with_bumblebee_checksum(self):
        doc = OGSolrDocument(data={'bumblebee_checksum': '123abc'})
        self.assertEqual(doc.bumblebee_checksum, '123abc')

    def test_without_containing_dossier(self):
        doc = OGSolrDocument(data={})
        self.assertEqual(doc.containing_dossier, None)

    def test_with_containing_dossier(self):
        doc = OGSolrDocument(data={'containing_dossier': 'My Dossier'})
        self.assertEqual(doc.containing_dossier, 'My Dossier')

    def test_croppeddescription_returns_snippets(self):
        doc = OGSolrDocument(data={'_snippets_': 'snippets'})
        obj = OGSolrContentListingObject(doc)
        self.assertEqual(obj.CroppedDescription(), 'snippets')

    def test_croppeddescription_without_snippets(self):
        doc = OGSolrDocument(data={'Description': 'My Description'})
        obj = OGSolrContentListingObject(doc)
        self.assertEqual(obj.CroppedDescription(), 'My Description')


class TestSolrBlobIndexingFunctional(SolrFunctionalTestCase):

    def setUp(self):
        super(TestSolrBlobIndexingFunctional, self).setUp()
        api.portal.set_registry_record(
            "opengever.dossier.interfaces.ITemplateFolderProperties.create_doc_properties",
            True)

    def make_path_param(self, *objects):
        """Build a paths:list request parameter, as expected by some views.
        """
        return {
            'paths:list': ['/'.join(obj.getPhysicalPath()) for obj in objects]}

    @browsing
    def test_blob_is_indexed_when_copy_pasting_dossier_containing_word_document(self, browser):
        browser.login()
        self.dossier = create(Builder('dossier'))
        self.document = create(Builder('document')
                               .titled(u'\xdcberpr\xfcfung XY')
                               .with_dummy_content()
                               .within(self.dossier))
        self.repofolder = create(Builder('repository'))

        with self.observe_children(self.repofolder) as children:
            browser.open(
                self.repofolder, view="copy_items",
                data=self.make_path_param(self.dossier))
            browser.css('#contentActionMenus a#paste').first.click()

        self.assertEqual(1, len(children['added']))
        created_dossier = children['added'].pop()
        created_document = created_dossier.listFolderContents()[0]

        self.commit_solr()
        self.assert_in_solr(created_document)
        searchable_text = solr_data_for(created_document, 'SearchableText')
        self.assertIsNotNone(searchable_text)
        self.assertIn(u'Test data\n\n', searchable_text)

    @browsing
    def test_blob_is_indexed_when_creating_dossier_with_template_containing_word_document(self, browser):
        api.portal.set_registry_record(
            "opengever.dossier.dossiertemplate.interfaces.IDossierTemplateSettings.is_feature_enabled",
            True)

        browser.login()

        self.repofolder = create(Builder('repository'))

        self.templates = create(
            Builder('templatefolder')
            .titled(u'Vorlagen')
            .having(id='vorlagen')
        )

        self.dossiertemplate = create(
            Builder('dossiertemplate')
            .titled(u'Bauvorhaben klein')
            .within(self.templates)
        )
        self.dossiertemplatedocument = create(
            Builder('document')
            .within(self.dossiertemplate)
            .titled(u'Werkst\xe4tte')
            .with_asset_file(u'vertragsentwurf.docx')
        )

        with self.observe_children(self.repofolder) as children:
            browser.open(self.repofolder)
            factoriesmenu.add('Dossier from template')
            token = browser.css(
                'input[name="form.widgets.template"]').first.attrib.get('value')
            browser.fill({'form.widgets.template': token}).submit()
            browser.click_on('Save')

        self.assertEqual(1, len(children['added']))
        created_dossier = children['added'].pop()
        created_document = created_dossier.listFolderContents()[0]

        self.commit_solr()
        self.assert_in_solr(created_document)
        searchable_text = solr_data_for(created_document, 'SearchableText')
        self.assertIsNotNone(searchable_text)
        self.assertIn(u'Vertragsentwurf', searchable_text)
