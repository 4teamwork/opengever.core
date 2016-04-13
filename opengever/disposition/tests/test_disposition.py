from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.testing import FunctionalTestCase


class TestDisposition(FunctionalTestCase):

    def setUp(self):
        super(TestDisposition, self).setUp()
        self.root = create(Builder('repository_root'))
        repository = create(Builder('repository').within(self.root))
        self.dossier1 = create(Builder('dossier').within(repository))
        self.dossier2 = create(Builder('dossier').within(repository))

    @browsing
    def test_can_be_added(self, browser):
        browser.login().open(self.root)
        factoriesmenu.add('Disposition')

        browser.fill({'Reference': 'Ablieferung X29238',
                      'Dossiers': [self.dossier1, self.dossier2]})

        browser.find('Save').click()

        self.assertEquals(['Item created'], info_messages())
