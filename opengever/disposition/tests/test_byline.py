from DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestDispositionByline(FunctionalTestCase):

    def setUp(self):
        super(TestDispositionByline, self).setUp()
        self.root = create(Builder('repository_root'))
        self.repository = create(Builder('repository').within(self.root))
        self.dossier1 = create(Builder('dossier')
                               .as_expired()
                               .within(self.repository))

    @browsing
    def test_shows_current_review_state_creation_and_modification_date(self, browser):
        disposition = create(Builder('disposition')
                             .having(dossiers=[self.dossier1])
                             .with_creation_date(DateTime(2016, 4, 10, 7, 25))
                             .with_modification_date(DateTime(2016, 4, 22, 22))
                             .within(self.root))

        browser.login().open(disposition)

        self.assertEquals(
            ['Created: Apr 10, 2016 07:25 AM',
             'State: disposition-state-in-progress',
             'Last modified: Apr 22, 2016 10:00 PM'],
            browser.css('#plone-document-byline li').text)
