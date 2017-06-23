from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from opengever.testing import obj2brain


class TestReferencePrefixUpdating(IntegrationTestCase):

    @browsing
    def test_reference_number_is_updated_in_catalog(self, browser):
        self.login(self.administrator)
        self.assertEquals('Client1 1.1', obj2brain(self.leaf_repository).reference)

        browser.login(self.administrator).open(self.leaf_repository, view='edit')
        browser.fill({'Reference Prefix': u'7'}).save()
        self.assertEquals('Client1 1.7', obj2brain(self.leaf_repository).reference)

    @browsing
    def test_reference_number_of_children_is_updated_in_catalog(self, browser):
        self.login(self.administrator)
        self.assertEqual(
            self.leaf_repository,
            aq_parent(aq_inner(self.dossier)),
            'Fixture: expected self.dossier to be within self.leaf_repository')
        self.assertEquals('Client1 1.1 / 1', obj2brain(self.dossier).reference)

        browser.login(self.administrator).open(self.leaf_repository, view='edit')
        browser.fill({'Reference Prefix': u'7'}).save()
        self.assertEquals('Client1 1.7 / 1', obj2brain(self.dossier).reference)
