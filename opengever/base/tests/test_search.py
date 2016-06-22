from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.core.testing import OPENGEVER_FUNCTIONAL_BUMBLEBEE_LAYER
from opengever.testing import FunctionalTestCase


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
