from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase
from opengever.testing import obj2brain


class TestReferencePrefixUpdating(FunctionalTestCase):

    def setUp(self):
        super(TestReferencePrefixUpdating, self).setUp()
        self.repository_root = create(Builder('repository_root'))
        self.repository_1 = create(Builder('repository')
                                   .within(self.repository_root)
                                   .titled(u'Repository A'))
        self.repository_1_1 = create(Builder('repository')
                                     .within(self.repository_1)
                                     .titled(u'Repository A'))
        self.dossier = create(Builder('dossier')
                              .within(self.repository_1_1))
        self.subdossier = create(Builder('dossier').within(self.dossier))
        self.document = create(Builder('document').within(self.subdossier))

    @browsing
    def test_reference_number_is_updated_in_catalog(self, browser):
        self.grant('Manager')
        browser.login().open(self.repository_1, view='edit')
        browser.fill({'Reference Prefix': u'6'})
        browser.find('Save').click()

        self.assertEquals('Client1 6', obj2brain(self.repository_1).reference)

    @browsing
    def test_reference_number_of_children_is_updated_in_catalog(self, browser):
        self.grant('Manager')
        browser.login().open(self.repository_1, view='edit')
        browser.fill({'Reference Prefix': u'6'})
        browser.find('Save').click()

        self.assertEquals('Client1 6.1',
                          obj2brain(self.repository_1_1).reference)
        self.assertEquals('Client1 6.1 / 1',
                          obj2brain(self.dossier).reference)
        self.assertEquals('Client1 6.1 / 1.1',
                          obj2brain(self.subdossier).reference)
        self.assertEquals('Client1 6.1 / 1.1 / 1',
                          obj2brain(self.document).reference)
