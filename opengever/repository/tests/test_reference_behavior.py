from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from ftw.testbrowser.pages import z3cform
from opengever.repository.behaviors.referenceprefix import IReferenceNumberPrefix
from opengever.repository.behaviors.referenceprefix import IReferenceNumberPrefixMarker
from opengever.testing import IntegrationTestCase
from zope.interface.verify import verifyObject


class TestReferenceBehavior(IntegrationTestCase):

    def test_repositories_provide_marker_interface(self):
        self.login(self.regular_user)
        self.assertTrue(IReferenceNumberPrefixMarker.providedBy(
            self.leaf_repofolder))
        verifyObject(IReferenceNumberPrefixMarker, self.leaf_repofolder)

    @browsing
    def test_set_next_reference_number_as_default_value(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.branch_repofolder)
        factoriesmenu.add('Repository Folder')
        self.assertEquals('2', browser.find('Reference number component').value)

    @browsing
    def test_using_already_used_prefix_is_not_possible(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.repository_root)
        factoriesmenu.add('Repository Folder')
        browser.fill({
            'Title (German)': u'Test repository',
            'Title (English)': u'Test repository',
            'Reference number component': '1',
        }).save()

        self.assertEquals(
            {'Reference number component': [
                'A repository folder with the same reference number already exists on the same level.']},
            z3cform.erroneous_fields(browser.forms['form']))

    @browsing
    def test_using_a_free_value_lower_than_the_next_one_is_valid(self, browser):
        self.login(self.administrator, browser)
        create(Builder('repository')
               .within(self.repository_root)
               .having(reference_number_prefix='27'))

        browser.open(self.repository_root)
        factoriesmenu.add('Repository Folder')
        browser.fill({
            'Title (German)': u'Test repository',
            'Title (English)': u'Test repository',
            'Reference number component': '26',
        }).save()
        statusmessages.assert_no_error_messages()

        prefix_adapter = IReferenceNumberPrefix(browser.context)
        self.assertEquals('26', prefix_adapter.reference_number_prefix)

    @browsing
    def test_works_also_with_alpha_numeric_prefixes(self, browser):
        self.login(self.administrator, browser)
        browser.open(self.repository_root)
        factoriesmenu.add('Repository Folder')
        browser.fill({
            'Title (German)': u'Test repository',
            'Title (English)': u'Test repository',
            'Reference number component': 'a1x10',
        }).save()
        statusmessages.assert_no_error_messages()

        prefix_adapter = IReferenceNumberPrefix(browser.context)
        self.assertEquals('a1x10', prefix_adapter.reference_number_prefix)
