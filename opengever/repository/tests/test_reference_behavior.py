from ftw.builder import Builder
from ftw.builder import create
from opengever.repository.behaviors.referenceprefix import IReferenceNumberPrefix
from opengever.repository.behaviors.referenceprefix import IReferenceNumberPrefixMarker
from opengever.repository.behaviors.referenceprefix import ReferenceNumberPrefixValidator
from opengever.testing import FunctionalTestCase
from zope.component import provideAdapter


class TestReferenceBehavior(FunctionalTestCase):
    """
    The reference number Behavior show a integer field (reference Number), the reference number field.
    The behavior set the default value to the next possible sequence number:
    """
    use_browser = True

    def setUp(self):
        super(TestReferenceBehavior, self).setUp()
        # Since plone tests sucks, we need to re-register
        # the reference number validator again.
        provideAdapter(ReferenceNumberPrefixValidator)

        self.grant('Manager')

        self.repo = create(Builder('repository'))

    def test_repositories_provided_referenceprefix_marker_interface(self):
        self.assertTrue(IReferenceNumberPrefixMarker.providedBy(self.repo))

    def test_set_next_reference_number_as_default_value(self):
        create(Builder('repository')
               .within(self.repo)
               .having(reference_number_prefix='5'))

        self.browser.open(
            '%s/++add++opengever.repository.repositoryfolder' % (
                self.repo.absolute_url()))

        reference_prefix = self.browser.control('Reference Prefix')
        self.assertEquals('6', reference_prefix.value)

    def test_using_allready_used_prefix_is_not_possible(self):
        create(Builder('repository')
               .within(self.repo)
               .having(reference_number_prefix='5'))

        self.browser.open(
            '%s/++add++opengever.repository.repositoryfolder' % (
                self.repo.absolute_url()))

        self.browser.fill({
            'Title': 'Test repository',
            'Reference Prefix': '5'})
        self.browser.click('Save')

        field_error_box = self.browser.css(
            '#formfield-form-widgets-IReferenceNumberPrefix-'
            'reference_number_prefix .error')[0]
        self.assertEquals(
            'Constraint not satisfied',
            field_error_box.plain_text())

    def test_using_a_free_value_lower_than_the_next_one_is_valid(self):
        create(Builder('repository')
               .within(self.repo)
               .having(reference_number_prefix='8'))
        create(Builder('repository')
               .within(self.repo)
               .having(reference_number_prefix='9'))

        self.browser.open(
            '%s/++add++opengever.repository.repositoryfolder' % (
                self.repo.absolute_url()))
        self.browser.fill({
            'Title': u'Test repository',
            'Reference Prefix': '7'})
        self.browser.click('Save')

        prefix_adapter = IReferenceNumberPrefix(self.repo.get('test-repository'))
        self.assertEquals('7', prefix_adapter.reference_number_prefix)

    def test_works_also_with_alpha_numeric_prefixes(self):
        create(Builder('repository')
               .within(self.repo)
               .having(reference_number_prefix='5'))

        self.browser.open(
            '%s/++add++opengever.repository.repositoryfolder' % (
                self.repo.absolute_url()))
        self.browser.fill({
            'Title': u'Test repository',
            'Reference Prefix': 'a1x10'})
        self.browser.click('Save')

        prefix_adapter = IReferenceNumberPrefix(self.repo.get('test-repository'))
        self.assertEquals('a1x10', prefix_adapter.reference_number_prefix)
