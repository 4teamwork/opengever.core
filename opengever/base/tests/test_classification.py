from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.base.behaviors.classification import IClassification
from opengever.base.behaviors.classification import IClassificationSettings
from opengever.base.behaviors.classification import PUBLIC_TRIAL_PRIVATE
from opengever.testing import IntegrationTestCase
from plone import api
from plone.dexterity.utils import createContentInContainer


class TestClassificationDefault(IntegrationTestCase):

    def get_classification(self, obj):
        field = IClassification['classification']
        return field.get(field.interface(obj))

    def set_classification(self, obj, value):
        field = IClassification['classification']
        field.set(field.interface(obj), value)

    def get_fti(self, portal_type):
        types_tool = api.portal.get_tool('portal_types')
        return types_tool[portal_type]

    @browsing
    def test_classification_default(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()

        value = self.get_classification(browser.context)
        self.assertEqual(u'unprotected', value)

    @browsing
    def test_classification_acquired_default(self, browser):
        self.login(self.regular_user, browser=browser)
        self.set_classification(self.leaf_repofolder, u'confidential')

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()

        value = self.get_classification(browser.context)
        self.assertEqual(u'confidential', value)

    @browsing
    def test_classification_acquires_default_with_quickupload(self, browser):
        self.login(self.regular_user, browser=browser)

        IClassification(self.dossier).classification = 'confidential'
        document = create(Builder('quickuploaded_document')
                          .within(self.dossier)
                          .with_data('text'))

        value = self.get_classification(document)
        self.assertEqual(u'confidential', value)

    @browsing
    def test_intermediate_folder_doesnt_break_default_aq(self, browser):
        # An intermediate folderish object that doesn't have the respective
        # field shouldn't break acquisition of the default
        self.login(self.manager, browser=browser)
        self.set_classification(self.leaf_repofolder, u'confidential')

        fti = self.get_fti('opengever.repository.repositoryfolder')
        fti.allowed_content_types = fti.allowed_content_types + ('Dummy',)
        dummy = createContentInContainer(self.leaf_repofolder, 'Dummy')

        self.login(self.regular_user, browser=browser)

        browser.open(dummy)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_classification(dossier)
        self.assertEqual(u'confidential', value)


class TestClassificationVocabulary(IntegrationTestCase):

    def setUp(self):
        super(TestClassificationVocabulary, self).setUp()
        self.field = IClassification['classification']

    def get_classification(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_classification(self, obj, value):
        self.field.set(self.field.interface(obj), value)

    @browsing
    def test_classification_default_choices(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        form_field = browser.find('Classification')
        self.assertEqual(
            ['unprotected', 'confidential', 'classified'],
            form_field.options_values)

    @browsing
    def test_aq_value_is_contained_in_choices_if_restricted(self, browser):
        self.login(self.regular_user, browser=browser)
        self.set_classification(self.leaf_repofolder, u'confidential')

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Classification')
        self.assertIn('confidential', form_field.options_values)

    @browsing
    def test_vocab_is_restricted_if_indicated_by_aq_value(self, browser):
        self.login(self.regular_user, browser=browser)
        self.set_classification(self.leaf_repofolder, u'confidential')

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Classification')
        self.assertSetEqual(
            set(['confidential', 'classified']),
            set(form_field.options_values))

    @browsing
    def test_acquired_value_is_suggested_as_default(self, browser):
        self.login(self.regular_user, browser=browser)

        self.set_classification(self.leaf_repofolder, u'confidential')

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Classification')
        self.assertEqual('confidential', form_field.value)
        # Default listed first
        self.assertEqual('confidential', form_field.options_values[0])

    @browsing
    def test_restriction_works_in_edit_form(self, browser):
        self.login(self.regular_user, browser=browser)

        self.set_classification(self.leaf_repofolder, u'confidential')

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()

        browser.click_on('Edit')
        form_field = browser.find('Classification')
        self.assertSetEqual(
            set(['confidential', 'classified']),
            set(form_field.options_values))


class TestClassificationPropagation(IntegrationTestCase):

    def setUp(self):
        super(TestClassificationPropagation, self).setUp()
        self.field = IClassification['classification']

    def get_classification(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_classification(self, obj, value):
        self.field.set(self.field.interface(obj), value)

    @browsing
    def test_change_propagates_to_children(self, browser):
        self.login(self.administrator, browser=browser)

        # Start with a loose classification
        self.set_classification(self.leaf_repofolder, u'unprotected')

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        # Dossier should have inherited classification from repofolder
        self.assertEqual(u'unprotected', self.get_classification(dossier))

        # Make classification more strict
        browser.open(self.leaf_repofolder, view='edit')
        browser.fill({'Classification': 'confidential'}).save()

        # Stricter classification should have propagated to dossier
        self.assertEqual(u'confidential', self.get_classification(dossier))

    @browsing
    def test_change_doesnt_propagate_if_old_value_still_valid(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier',
                      'Classification': 'confidential'}).save()

        dossier = browser.context
        self.assertEqual(u'confidential', self.get_classification(dossier))

        browser.open(self.leaf_repofolder, view='edit')
        browser.fill({'Classification': 'unprotected'}).save()

        self.assertEqual(u'confidential', self.get_classification(dossier))

    @browsing
    def test_propagation_is_depth_limited(self, browser):
        """Propagation of classification is depth limited to 2 levels.
        Not sure why this was implemented this way, but here we test for it.
        """
        self.login(self.administrator, browser=browser)

        # Start with a loose classification
        self.set_classification(self.branch_repofolder, u'unprotected')
        repofolder2 = create(Builder('repository').within(self.branch_repofolder))
        repofolder3 = create(Builder('repository').within(repofolder2))

        browser.open(repofolder3)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        # Dossier should have inherited classification from repofolder2
        self.assertEqual(u'unprotected', self.get_classification(dossier))

        # Make classification more strict on top level repofolder
        browser.open(self.branch_repofolder, view='edit')
        browser.fill({'Classification': 'confidential'}).save()

        # Stricter classification should have propagated to repofolder2, but
        # not dossier (because of depth limitation)
        self.assertEqual(u'confidential', self.get_classification(repofolder2))
        self.assertEqual(u'unprotected', self.get_classification(dossier))


class TestPrivacyLayerDefault(IntegrationTestCase):

    def setUp(self):
        super(TestPrivacyLayerDefault, self).setUp()
        self.field = IClassification['privacy_layer']

    def get_privacy_layer(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_privacy_layer(self, obj, value):
        self.field.set(self.field.interface(obj), value)

    def get_fti(self, portal_type):
        types_tool = api.portal.get_tool('portal_types')
        return types_tool[portal_type]

    @browsing
    def test_privacy_layer_default(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()

        value = self.get_privacy_layer(browser.context)
        self.assertEqual(u'privacy_layer_no', value)

    @browsing
    def test_privacy_layer_acquired_default(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.leaf_repofolder)
        self.set_privacy_layer(self.leaf_repofolder, u'privacy_layer_yes')
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_privacy_layer(dossier)
        self.assertEqual(u'privacy_layer_yes', value)

    @browsing
    def test_intermediate_folder_doesnt_break_default_aq(self, browser):
        self.login(self.regular_user, browser=browser)

        # An intermediate folderish object that doesn't have the respective
        # field shouldn't break acquisition of the default
        self.set_privacy_layer(self.leaf_repofolder, u'privacy_layer_yes')

        fti = self.get_fti('opengever.repository.repositoryfolder')
        fti.allowed_content_types = fti.allowed_content_types + ('Dummy',)

        dummy = createContentInContainer(self.leaf_repofolder, 'Dummy')

        browser.open(dummy)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()

        value = self.get_privacy_layer(browser.context)
        self.assertEqual(u'privacy_layer_yes', value)


class TestPrivacyLayerVocabulary(IntegrationTestCase):

    def setUp(self):
        super(TestPrivacyLayerVocabulary, self).setUp()
        self.field = IClassification['privacy_layer']

    def get_privacy_layer(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_privacy_layer(self, obj, value):
        self.field.set(self.field.interface(obj), value)

    @browsing
    def test_privacy_layer_default_choices(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        form_field = browser.find('Privacy protection')
        self.assertEqual(
            ['privacy_layer_no', 'privacy_layer_yes'],
            form_field.options_values)

    @browsing
    def test_aq_value_is_contained_in_choices_if_restricted(self, browser):
        self.login(self.regular_user, browser=browser)

        self.set_privacy_layer(self.leaf_repofolder, u'privacy_layer_yes')

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Privacy protection')
        self.assertIn('privacy_layer_yes', form_field.options_values)

    @browsing
    def test_vocab_is_restricted_if_indicated_by_aq_value(self, browser):
        self.login(self.regular_user, browser=browser)

        self.set_privacy_layer(self.leaf_repofolder, u'privacy_layer_yes')

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Privacy protection')
        self.assertSetEqual(
            set(['privacy_layer_yes']),
            set(form_field.options_values))

    @browsing
    def test_acquired_value_is_suggested_as_default(self, browser):
        self.login(self.regular_user, browser=browser)

        self.set_privacy_layer(self.leaf_repofolder, u'privacy_layer_yes')

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Privacy protection')

        self.assertEqual('privacy_layer_yes', form_field.value)
        # Default listed first
        self.assertEqual('privacy_layer_yes', form_field.options_values[0])

    @browsing
    def test_restriction_works_in_edit_form(self, browser):
        self.login(self.regular_user, browser=browser)
        self.set_privacy_layer(self.leaf_repofolder, u'privacy_layer_yes')

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()

        browser.click_on('Edit')
        form_field = browser.find('Privacy protection')
        self.assertSetEqual(
            set(['privacy_layer_yes']),
            set(form_field.options_values))


class TestPrivacyLayerPropagation(IntegrationTestCase):

    def setUp(self):
        super(TestPrivacyLayerPropagation, self).setUp()
        self.field = IClassification['privacy_layer']

    def get_privacy_layer(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_privacy_layer(self, obj, value):
        self.field.set(self.field.interface(obj), value)

    @browsing
    def test_change_propagates_to_children(self, browser):
        self.login(self.administrator, browser=browser)

        # Start with a loose privacy layer
        self.set_privacy_layer(self.leaf_repofolder, u'privacy_layer_no')

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()

        dossier = browser.context

        # Dossier should have inherited privacy layer from repofolder
        self.assertEqual(u'privacy_layer_no', self.get_privacy_layer(dossier))

        # Make privacy layer more strict
        browser.open(self.leaf_repofolder, view='edit')
        browser.fill({'Privacy protection': 'privacy_layer_yes'}).save()

        # Stricter privacy layer should have propagated to dossier
        self.assertEqual(u'privacy_layer_yes', self.get_privacy_layer(dossier))

    @browsing
    def test_change_doesnt_propagate_if_old_value_still_valid(self, browser):
        self.login(self.administrator, browser=browser)

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({
            'Title': 'My Dossier',
            'Privacy protection': 'privacy_layer_yes'}).save()
        dossier = browser.context

        self.assertEqual(u'privacy_layer_yes', self.get_privacy_layer(dossier))

        browser.open(self.leaf_repofolder, view='edit')
        browser.fill({'Privacy protection': 'privacy_layer_no'}).save()

        self.assertEqual(u'privacy_layer_yes', self.get_privacy_layer(dossier))

    @browsing
    def test_propagation_is_depth_limited(self, browser):
        """Propagation of privacy layer is depth limited to 2 levels.
        Not sure why this was implemented this way, but here we test for it.
        """
        self.login(self.administrator, browser=browser)

        # Start with a loose privacy layer
        self.set_privacy_layer(self.leaf_repofolder, u'privacy_layer_no')
        repofolder2 = create(Builder('repository').within(self.leaf_repofolder))
        repofolder3 = create(Builder('repository').within(repofolder2))

        browser.open(repofolder3)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        # Dossier should have inherited privacy layer from repofolder2
        self.assertEqual(u'privacy_layer_no', self.get_privacy_layer(dossier))

        # Reduce privacy layer on top level repofolder
        browser.open(self.leaf_repofolder, view='edit')
        browser.fill({'Privacy protection': 'privacy_layer_yes'}).save()

        # Reduced privacy layer should have propagated to repofolder2, but
        # not dossier (because of depth limitation)
        self.assertEqual(
            u'privacy_layer_yes', self.get_privacy_layer(repofolder2))
        self.assertEqual(
            u'privacy_layer_no', self.get_privacy_layer(dossier))


class TestPublicTrialField(IntegrationTestCase):

    def setUp(self):
        super(TestPublicTrialField, self).setUp()
        self.field = IClassification['public_trial']

    def get_public_trial(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_public_trial(self, obj, value):
        self.field.set(self.field.interface(obj), value)

    @browsing
    def test_public_trial_default(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier)
        factoriesmenu.add(u'Document')
        browser.fill({'Title': 'My Document'}).save()
        document = browser.context

        value = self.get_public_trial(document)
        self.assertEqual(u'unchecked', value)

    @browsing
    def test_public_trial_default_is_configurable(self, browser):
        self.login(self.regular_user, browser=browser)

        api.portal.set_registry_record(
            'public_trial_default_value', PUBLIC_TRIAL_PRIVATE,
            interface=IClassificationSettings)

        browser.open(self.dossier)
        factoriesmenu.add(u'Document')
        browser.fill({'Title': 'My Document'}).save()
        document = self.dossier.objectValues()[-1]

        value = self.get_public_trial(document)
        self.assertEqual(PUBLIC_TRIAL_PRIVATE, value)

    @browsing
    def test_public_trial_default_choices(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.dossier)
        factoriesmenu.add(u'Document')
        form_field = browser.find('Public access level')
        self.assertEqual(
            ['unchecked', 'public', 'limited-public', 'private'],
            form_field.options_values)

    @browsing
    def test_public_trial_is_no_longer_restricted_on_subitems(self, browser):
        self.login(self.regular_user, browser=browser)
        self.set_public_trial(self.dossier, PUBLIC_TRIAL_PRIVATE)

        browser.open(self.dossier)
        factoriesmenu.add(u'Document')
        form_field = browser.find('Public access level')
        self.assertEqual(
            ['unchecked', 'public', 'limited-public', 'private'],
            form_field.options_values)

    @browsing
    def test_public_trial_is_hidden_on_dossier(self, browser):
        self.login(self.regular_user, browser=browser)

        selector = ('#formfield-form-widgets-IClassification-public_trial '
                    '.hidden-widget')
        selector2 = ('#formfield-form-widgets-IClassification-public_trial_'
                     'statement .hidden-widget')

        browser.open(self.leaf_repofolder)
        factoriesmenu.add('Business Case Dossier')
        self.assertTrue(browser.css(selector), 'Public trial should be hidden')
        self.assertTrue(browser.css(selector2),
                        'Public access level statement should be hidden')

        browser.open(self.dossier, view='edit')
        self.assertTrue(browser.css(selector), 'Public trial should be hidden')
        self.assertTrue(browser.css(selector2),
                        'Public access level statement should be hidden')

    @browsing
    def test_public_trial_is_hidden_on_repofolder(self, browser):
        self.login(self.administrator, browser=browser)

        selector = ('#formfield-form-widgets-IClassification-public_trial '
                    '.hidden-widget')
        selector2 = ('#formfield-form-widgets-IClassification-public_trial_'
                     'statement .hidden-widget')

        browser.open(self.branch_repofolder)
        factoriesmenu.add('Repository Folder')
        self.assertTrue(browser.css(selector), 'Public trial should be hidden')
        self.assertTrue(browser.css(selector2),
                        'Public access level statement should be hidden')

        browser.visit(self.leaf_repofolder, view='edit')
        self.assertTrue(browser.css(selector), 'Public trial should be hidden')
        self.assertTrue(browser.css(selector2),
                        'Public access level statement should be hidden')


class TestChangesToPublicTrialAreJournalized(IntegrationTestCase):

    @browsing
    def test_regular_edit_form_journalizes_changes(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.document, view='edit')
        browser.fill({'Public access level': 'public'}).save()

        self.assert_journal_entry(
            self.document, 'Public trial modified',
            u'Public trial changed to "public".')

    @browsing
    def test_public_trial_edit_form_journalizes_changes(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.document, view='edit_public_trial')
        browser.fill({'Public access level': 'public'}).save()

        self.assert_journal_entry(
            self.document, 'Public trial modified',
            u'Public trial changed to "public".')
