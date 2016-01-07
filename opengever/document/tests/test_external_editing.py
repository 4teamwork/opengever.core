from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.core import LIB_REQUESTS
from ftw.testbrowser.pages import factoriesmenu
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ZSERVER_TESTING
from opengever.testing import FunctionalTestCase


class TestExternalEditing(FunctionalTestCase):

    # WebDAV stuff and streaming responses don't work with mechanize - so we
    # boot an actual ZServer and do real requests using the `requests` lib
    layer = OPENGEVER_FUNCTIONAL_ZSERVER_TESTING

    @browsing
    def test_filename_is_included_in_zem(self, browser):
        dossier = create(Builder('dossier'))
        browser.login().open(dossier.absolute_url())

        factoriesmenu.add('Document')
        browser.fill({'File': (
            'Lorem Ipsum', 'word.doc', 'application/msword')}
        ).save()

        doc = browser.context.restrictedTraverse('document-1')
        browser.open(doc, view='external_edit', library=LIB_REQUESTS)

        metadata, body = browser.contents.split('\n\n')
        self.assertIn('filename:word.doc', metadata.split('\n'))
