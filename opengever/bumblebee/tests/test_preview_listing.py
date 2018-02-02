from ftw.testbrowser import browsing
from opengever.bumblebee.browser.preview_listing import PreviewListing
from opengever.bumblebee.browser.preview_listing import PreviewListingBrains
from opengever.bumblebee.browser.preview_listing import PreviewListingObjects
from opengever.testing import IntegrationTestCase


class TestPreviewListing(IntegrationTestCase):

    @browsing
    def test_renders_container(self, browser):
        self.login(self.dossier_responsible, browser)
        view = self.dossier.restrictedTraverse('tabbedview_view-overview')
        fetch_url = self.dossier.absolute_url() + '/tabbedview_view-overview/fetch'
        listing = (PreviewListing(view)
                   .for_objects([self.document,
                                 self.subdocument,
                                 self.taskdocument])
                   .with_fetch_url(fetch_url))
        browser.open_html(listing.render())

        self.assertEqual(1, len(browser.css('.preview-listing')))
        self.assertDictEqual(
            {'class': 'preview-listing',
             'data-number-of-documents': '3',
             'data-fetch-url': fetch_url},
            dict(browser.css('.preview-listing').first.attrib))

    @browsing
    def test_renders_document_items(self, browser):
        self.login(self.dossier_responsible, browser)
        view = self.dossier.restrictedTraverse('tabbedview_view-overview')
        fetch_url = self.dossier.absolute_url() + '/tabbedview_view-overview/fetch'
        listing = (PreviewListing(view)
                   .for_objects([self.document,
                                 self.subdocument,
                                 self.taskdocument])
                   .with_fetch_url(fetch_url))
        browser.open_html(listing.render())

        self.assertEqual(3, len(browser.css('div.showroom-item')))

        self.assertDictEqual(
            {'id': 'createtreatydossiers000000000002',
             'class': 'imageContainer showroom-item',
             'data-showroom-target': (
                 self.document.absolute_url() + '/@@bumblebee-overlay-listing'),
             'data-showroom-title': u'Vertr\xe4gsentwurf'},
            dict(browser.css('div.showroom-item').first.attrib))

        self.assertDictEqual(
            {'class': 'file-mimetype icon-docx'},
            dict(browser.css('div.showroom-item > span').first.attrib))

        img_attrs = dict(browser.css('div.showroom-item > img').first.attrib)
        for e in ['src', 'data-bumblebee-src', 'data-bumblebee-checksum']:
            img_attrs.pop(e)
        self.assertDictEqual(
            {'class': 'file-preview bumblebee-thumbnail',
             'alt': u'Vertr\xe4gsentwurf'},
            img_attrs)

        self.assertEqual(
            u'Vertr\xe4gsentwurf',
            browser.css('div.showroom-item > div.bumblebeeTitle').first.text)

    @browsing
    def test_fetch_more(self, browser):
        self.login(self.dossier_responsible, browser)
        view = self.dossier.restrictedTraverse('tabbedview_view-overview')
        fetch_url = self.dossier.absolute_url() + '/tabbedview_view-overview/fetch'
        listing = (PreviewListing(view)
                   .for_objects([self.document,
                                 self.subdocument,
                                 self.taskdocument])
                   .with_fetch_url(fetch_url)
                   .with_batchsize(2))
        browser.open_html(listing.render())
        self.assertEqual(2, len(browser.css('div.showroom-item')))
        self.request.form['documentPointer'] = 2
        browser.open_html(listing.fetch())
        self.assertEqual(1, len(browser.css('div.showroom-item')))

    def test_PreviewListingObjects_vs_PreviewListingBrains(self):
        self.login(self.dossier_responsible)
        objects = PreviewListingObjects([self.document])
        brains = PreviewListingBrains([self.object_to_brain(self.document)])
        self.assertEquals(objects.get_infos_for(objects.get_batch(0, 1)[0]),
                          brains.get_infos_for(brains.get_batch(0, 1)[0]))
