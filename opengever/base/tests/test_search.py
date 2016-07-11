from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.testing import FunctionalTestCase
from plone import api
from zope.component import getMultiAdapter


class TestOpengeverSearch(FunctionalTestCase):

    def test_types_filters_list_is_limited_to_main_types(self):
        create(Builder('repository'))
        create(Builder('repository_root'))
        create(Builder('dossier'))
        create(Builder('document'))
        create(Builder('mail'))
        create(Builder('task'))
        create(Builder('inbox'))
        create(Builder('forwarding'))
        create(Builder('contactfolder'))
        create(Builder('contact'))

        self.assertItemsEqual(
            ['opengever.task.task', 'ftw.mail.mail',
             'opengever.document.document', 'opengever.inbox.forwarding',
             'opengever.dossier.businesscasedossier'],
            self.portal.unrestrictedTraverse('@@search').types_list())

    @browsing
    def test_batch_size_is_set_to_25(self, browser):
        for i in range(0, 30):
            create(Builder('dossier').titled(u'Test'))

        browser.login().open(self.portal, view='search')
        self.assertEqual(25, len(browser.css('dl.searchResults dt')))

    @browsing
    def test_no_bubmlebee_preview_rendered_when_feature_not_enabled(self, browser):
        browser.login().open(self.portal, view='search')
        self.assertEqual(0, len(browser.css('.searchImage')))


class TestBumblebeePreview(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER

    @browsing
    def test_link_previews_to_bumblebee_overlay_listing(self, browser):
        create(Builder('document')
               .titled(u'Foo Document')
               .with_dummy_content())

        browser.login().open(self.portal, view='search')
        browser.fill({'Search Site': 'Foo Document'}).submit()

        self.assertEqual(
            'http://nohost/plone/document-1/@@bumblebee-overlay-listing',
            browser.css('.showroom-item').first.get('data-showroom-target'))

    @browsing
    def test_only_bumblebeeable_content_opens_in_overlay(self, browser):
        dossier = create(Builder('dossier')
                         .titled(u'Foo Dossier'))
        create(Builder('document')
               .titled(u'Foo Document')
               .with_dummy_content()
               .within(dossier))

        browser.login().open(self.portal, view='search')
        browser.fill({'SearchableText': 'Foo*'}).submit()

        results = browser.css('.searchResults .searchItem dt a')
        self.assertEqual(
            ['Foo Dossier', 'Foo Document'],
            results.text)
        self.assertEqual(['state-dossier-state-active'],
                         results[0].classes)
        self.assertEqual(['state-document-state-draft', 'showroom-item'],
                         results[1].classes)

    @browsing
    def test_batch_size_is_available_in_template(self, browser):
        dossier = create(Builder('dossier')
                         .titled(u'Foo Dossier'))
        create(Builder('document')
               .titled(u'Foo Document')
               .with_dummy_content()
               .within(dossier))

        browser.login().open(self.portal, view='search')
        batch_size = browser.css('#search-results').first.attrib.get('data-batch-size')

        self.assertEqual(
            25, int(batch_size),
            'The batch-size data atribute should be on the tag')

    @browsing
    def test_number_of_documents_is_available_in_template(self, browser):
        dossier = create(Builder('dossier')
                         .titled(u'Foo Dossier'))

        create(Builder('document')
               .titled(u'Foo Document')
               .with_dummy_content()
               .within(dossier))

        create(Builder('dossier').within(dossier))

        browser.login().open(self.portal, view='search')

        number_of_documents = browser.css(
            '#search-results .searchResults').first.attrib.get('data-number-of-documents')

        self.assertEqual(
            1, int(number_of_documents),
            'The number_of_documents data should be set to the amount of'
            'of found bumblebeeable objects.')

    @browsing
    def test_set_showroom_vars_correctly(self, browser):
        catalog = api.portal.get_tool('portal_catalog')

        base = create(Builder('dossier'))

        search_view = getMultiAdapter((self.portal, self.request), name="search")

        # Batch 1
        create(Builder('document').within(base).titled(u'A Foo'))
        create(Builder('dossier').within(base).titled(u'B Foo'))

        # Batch 2
        create(Builder('document').within(base).titled(u'C Foo'))
        create(Builder('document').within(base).titled(u'D Foo'))

        # Batch 3
        create(Builder('dossier').within(base).titled(u'E Foo'))
        create(Builder('document').within(base).titled(u'F Foo'))

        brains = catalog({'sort_on': 'sortable_title', 'SearchableText':"Foo"})

        search_view.calculate_showroom_configuration(brains, b_start=0)
        self.assertEqual(4, search_view.number_of_documents)
        self.assertEqual(0, search_view.offset)

        search_view.calculate_showroom_configuration(brains, b_start=3)
        self.assertEqual(4, search_view.number_of_documents)
        self.assertEqual(2, search_view.offset)

        search_view.calculate_showroom_configuration(brains, b_start=5)
        self.assertEqual(4, search_view.number_of_documents)
        self.assertEqual(3, search_view.offset)
