from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.repository.behaviors.referenceprefix import IReferenceNumberPrefix
from opengever.repository.behaviors.referenceprefix import IReferenceNumberPrefixMarker
from opengever.testing import add_languages
from opengever.testing import FunctionalTestCase
from ftw.testbrowser.pages import factoriesmenu


class TestReferenceBehavior(FunctionalTestCase):
    """
    The reference number Behavior show a integer field (reference Number), the reference number field.
    The behavior set the default value to the next possible sequence number:
    """

    def setUp(self):
        super(TestReferenceBehavior, self).setUp()

        add_languages(['de-ch'])
        self.repo = create(Builder('repository'))

        self.grant('Administrator')

    def test_repositories_provided_referenceprefix_marker_interface(self):
        self.assertTrue(IReferenceNumberPrefixMarker.providedBy(self.repo))

    @browsing
    def test_set_next_reference_number_as_default_value(self, browser):
        create(Builder('repository')
               .within(self.repo)
               .having(reference_number_prefix='5'))

        browser.login().open(self.repo)
        factoriesmenu.add('RepositoryFolder')

        self.assertEquals('6', browser.find('Reference Prefix').value)

    @browsing
    def test_using_allready_used_prefix_is_not_possible(self, browser):
        create(Builder('repository')
               .within(self.repo)
               .having(reference_number_prefix='5'))

        browser.login().open(self.repo)
        factoriesmenu.add('RepositoryFolder')
        browser.fill({'Title': 'Test repository', 'Reference Prefix': '5'})
        browser.click_on('Save')

        self.assertEquals(
            ['A Sibling with the same reference number is existing'],
            browser.css('#formfield-form-widgets-IReferenceNumberPrefix'
                        '-reference_number_prefix .error').text)

    @browsing
    def test_using_a_free_value_lower_than_the_next_one_is_valid(self, browser):
        create(Builder('repository')
               .within(self.repo)
               .having(reference_number_prefix='8'))
        create(Builder('repository')
               .within(self.repo)
               .having(reference_number_prefix='9'))

        browser.login().open(self.repo)
        factoriesmenu.add('RepositoryFolder')
        browser.fill({'Title': u'Test repository',
                      'Reference Prefix': '7'})
        browser.click_on('Save')

        prefix_adapter = IReferenceNumberPrefix(self.repo.get('test-repository'))
        self.assertEquals('7', prefix_adapter.reference_number_prefix)

    @browsing
    def test_works_also_with_alpha_numeric_prefixes(self, browser):
        create(Builder('repository')
               .within(self.repo)
               .having(reference_number_prefix='5'))

        browser.login().open(self.repo)
        factoriesmenu.add('RepositoryFolder')
        browser.fill({'Title': u'Test repository',
                      'Reference Prefix': 'a1x10'})
        browser.click_on('Save')

        prefix_adapter = IReferenceNumberPrefix(self.repo.get('test-repository'))
        self.assertEquals('a1x10', prefix_adapter.reference_number_prefix)
