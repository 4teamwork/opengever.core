from Acquisition import aq_parent
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.base.behaviors.classification import CLASSIFICATION_UNPROTECTED
from opengever.base.behaviors.classification import IClassification
from opengever.base.behaviors.classification import IClassificationSettings
from opengever.base.behaviors.classification import PUBLIC_TRIAL_PRIVATE
from opengever.testing import IntegrationTestCase
from plone import api
from plone.dexterity.utils import createContentInContainer
import json


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

    @browsing
    def test_intermediate_obj_with_missing_attr_doesnt_break_default_aq(self, browser):
        # An intermediate object with the field in its schema, but missing the
        # actual attribute shouldn't break acquisition of the default
        self.login(self.regular_user, browser=browser)

        parent_folder = aq_parent(self.leaf_repofolder)
        self.set_classification(parent_folder, u'confidential')

        del self.leaf_repofolder.classification

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()

        value = self.get_classification(browser.context)
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
        self.assertItemsEqual(
            ['classified', 'confidential', 'unprotected'],
            form_field.options_values)

    @browsing
    def test_acquired_value_is_suggested_as_default(self, browser):
        self.login(self.regular_user, browser=browser)

        self.set_classification(self.leaf_repofolder, u'confidential')
        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Classification')
        self.assertEqual('confidential', form_field.value)

    @browsing
    def test_change_does_not_propagate_to_children(self, browser):
        self.login(self.administrator, browser=browser)

        # Start with a loose classification
        self.assertEqual(u'unprotected',
                         self.get_classification(self.branch_repofolder))
        self.assertEqual(u'unprotected',
                         self.get_classification(self.leaf_repofolder))
        self.assertEqual(u'unprotected',
                         self.get_classification(self.dossier))
        self.assertEqual(u'unprotected',
                         self.get_classification(self.document))

        # Make classification more strict
        browser.open(self.branch_repofolder, view='edit')
        browser.fill({'Classification': 'confidential'}).save()

        self.assertEqual(u'confidential',
                         self.get_classification(self.branch_repofolder))
        self.assertEqual(u'unprotected',
                         self.get_classification(self.leaf_repofolder))
        self.assertEqual(u'unprotected',
                         self.get_classification(self.dossier))
        self.assertEqual(u'unprotected',
                         self.get_classification(self.document))


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
    def test_acquired_value_is_suggested_as_default(self, browser):
        self.login(self.regular_user, browser=browser)

        self.set_privacy_layer(self.leaf_repofolder, u'privacy_layer_yes')

        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Privacy protection')

        self.assertEqual('privacy_layer_yes', form_field.value)

    @browsing
    def test_change_does_not_propagate_to_children(self, browser):
        self.login(self.administrator, browser=browser)

        # Start with a loose classification
        self.assertEqual(u'privacy_layer_no',
                         self.get_privacy_layer(self.branch_repofolder))
        self.assertEqual(u'privacy_layer_no',
                         self.get_privacy_layer(self.leaf_repofolder))
        self.assertEqual(u'privacy_layer_no',
                         self.get_privacy_layer(self.dossier))
        self.assertEqual(u'privacy_layer_no',
                         self.get_privacy_layer(self.document))

        # Make classification more strict
        browser.open(self.branch_repofolder, view='edit')
        browser.fill({'Privacy protection': 'privacy_layer_yes'}).save()

        self.assertEqual(u'privacy_layer_yes',
                         self.get_privacy_layer(self.branch_repofolder))
        self.assertEqual(u'privacy_layer_no',
                         self.get_privacy_layer(self.leaf_repofolder))
        self.assertEqual(u'privacy_layer_no',
                         self.get_privacy_layer(self.dossier))
        self.assertEqual(u'privacy_layer_no',
                         self.get_privacy_layer(self.document))


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
        form_field = browser.find('Disclosure status')
        self.assertEqual(
            ['unchecked', 'public', 'limited-public', 'private'],
            form_field.options_values)

    @browsing
    def test_public_trial_is_no_longer_restricted_on_subitems(self, browser):
        self.login(self.regular_user, browser=browser)
        self.set_public_trial(self.dossier, PUBLIC_TRIAL_PRIVATE)

        browser.open(self.dossier)
        factoriesmenu.add(u'Document')
        form_field = browser.find('Disclosure status')
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
                        'Disclosure status statement should be hidden')

        browser.open(self.dossier, view='edit')
        self.assertTrue(browser.css(selector), 'Public trial should be hidden')
        self.assertTrue(browser.css(selector2),
                        'Disclosure status statement should be hidden')

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
                        'Disclosure status statement should be hidden')

        browser.visit(self.leaf_repofolder, view='edit')
        self.assertTrue(browser.css(selector), 'Public trial should be hidden')
        self.assertTrue(browser.css(selector2),
                        'Disclosure status statement should be hidden')


class TestChangesToPublicTrialAreJournalized(IntegrationTestCase):

    @browsing
    def test_regular_edit_form_journalizes_changes(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.document, view='edit')
        browser.fill({'Disclosure status': 'public'}).save()

        self.assert_journal_entry(
            self.document, 'Public trial modified',
            u'Disclosure status changed to "public".')

    @browsing
    def test_public_trial_edit_form_journalizes_changes(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.document, view='edit_public_trial')
        browser.fill({'Disclosure status': 'public'}).save()

        self.assert_journal_entry(
            self.document, 'Public trial modified',
            u'Disclosure status changed to "public".')


class TestClassificationFieldsAreProtected(IntegrationTestCase):

    @browsing
    def test_fields_are_only_visible_on_add_form_if_permission_available(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.leaf_repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        self.assertIsNotNone(browser.forms['form'].find_field('Classification'))
        self.assertIsNotNone(browser.forms['form'].find_field('Privacy protection'))

        browser.css('#form-buttons-cancel').first.click()

        self.leaf_repofolder.manage_permission("Edit lifecycle and classification", roles=[])
        factoriesmenu.add(u'Business Case Dossier')
        self.assertIsNone(browser.forms['form'].find_field('Classification'))
        self.assertIsNone(browser.forms['form'].find_field('Privacy protection'))

    @browsing
    def test_fields_are_only_visible_on_edit_form_if_permission_available(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.dossier, view='edit')
        self.assertIsNotNone(browser.forms['form'].find_field('Classification'))
        self.assertIsNotNone(browser.forms['form'].find_field('Privacy protection'))

        browser.css('#form-buttons-cancel').first.click()

        self.leaf_repofolder.manage_permission("Edit lifecycle and classification", roles=[])
        browser.open(self.dossier, view='edit')
        self.assertIsNone(browser.forms['form'].find_field('Classification'))
        self.assertIsNone(browser.forms['form'].find_field('Privacy protection'))

    @browsing
    def test_create_dossier_via_api_only_overwrites_classification_fields_if_permission_available(self, browser):
        self.login(self.regular_user, browser)
        self.assertEqual(u'unprotected', IClassification(self.leaf_repofolder).classification)
        self.assertEqual(u'privacy_layer_no', IClassification(self.leaf_repofolder).privacy_layer)

        payload = {
            u'@type': u'opengever.dossier.businesscasedossier',
            u'responsible': self.regular_user.id,
            u'title': u'Sanierung B\xe4rengraben 2016',
            u'classification': u'confidential',
            u'privacy_layer': u'privacy_layer_yes',
        }
        with self.observe_children(self.leaf_repofolder) as children:
            browser.open(self.leaf_repofolder, data=json.dumps(payload),
                         method='POST', headers=self.api_headers)

        self.assertEqual(1, len(children['added']))
        dossier = children['added'].pop()

        self.assertEqual(u'confidential', IClassification(dossier).classification)
        self.assertEqual(u'privacy_layer_yes', IClassification(dossier).privacy_layer)

        self.leaf_repofolder.manage_permission("Edit lifecycle and classification", roles=[])
        with self.observe_children(self.leaf_repofolder) as children:
            browser.open(self.leaf_repofolder, data=json.dumps(payload),
                         method='POST', headers=self.api_headers)

        self.assertEqual(1, len(children['added']))
        dossier = children['added'].pop()

        self.assertEqual(u'unprotected', IClassification(dossier).classification)
        self.assertEqual(u'privacy_layer_no', IClassification(dossier).privacy_layer)

    @browsing
    def test_edit_dossier_via_api_overwrites_classification_fields_if_permission_available(self, browser):
        self.login(self.regular_user, browser)
        self.assertEqual(u'unprotected', IClassification(self.dossier).classification)
        self.assertEqual(u'privacy_layer_no', IClassification(self.dossier).privacy_layer)

        payload = {
            u'classification': u'confidential',
            u'privacy_layer': u'privacy_layer_yes',
        }
        browser.open(self.dossier, data=json.dumps(payload),
                     method='PATCH', headers=self.api_headers)

        self.assertEqual(u'confidential', IClassification(self.dossier).classification)
        self.assertEqual(u'privacy_layer_yes', IClassification(self.dossier).privacy_layer)

    @browsing
    def test_edit_dossier_via_api_does_not_overwrite_classification_fields_if_permission_missing(self, browser):
        self.login(self.regular_user, browser)
        self.assertEqual(u'unprotected', IClassification(self.dossier).classification)
        self.assertEqual(u'privacy_layer_no', IClassification(self.dossier).privacy_layer)

        payload = {
            u'classification': u'confidential',
            u'privacy_layer': u'privacy_layer_yes',
        }
        self.dossier.manage_permission("Edit lifecycle and classification", roles=[])
        browser.open(self.dossier, data=json.dumps(payload),
                     method='PATCH', headers=self.api_headers)

        self.assertEqual(u'unprotected', IClassification(self.dossier).classification)
        self.assertEqual(u'privacy_layer_no', IClassification(self.dossier).privacy_layer)

    @browsing
    def test_fill_classification(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.leaf_repofolder)
        api.portal.set_registry_record(
            name='hidden_classifications', interface=IClassificationSettings, value=[])

        # Reset cached hidden_terms in the vocabulary
        IClassification['classification'].vocabulary.hidden_terms = []

        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Classification')
        self.assertEqual(
            ['unprotected', 'confidential', 'classified'],
            form_field.options_values)

        browser.fill({'Classification': CLASSIFICATION_UNPROTECTED})
        browser.click_on('Save')

        self.assertEquals(u'unprotected', IClassification(self.leaf_repofolder).classification)
