from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.base.behaviors import classification
from opengever.base.behaviors.classification import IClassification
from opengever.base.behaviors.classification import IClassificationSettings
from opengever.journal.browser import JournalHistory
from opengever.testing import FunctionalTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.utils import createContentInContainer
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.i18n import translate
import transaction


class TestClassificationDefault(FunctionalTestCase):

    def setUp(self):
        super(TestClassificationDefault, self).setUp()
        self.repofolder = create(Builder('repository'))
        self.field = IClassification['classification']

    def get_classification(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_classification(self, obj, value):
        self.field.set(self.field.interface(obj), value)
        transaction.commit()

    def get_fti(self, portal_type):
        types_tool = api.portal.get_tool('portal_types')
        return types_tool[portal_type]

    @browsing
    def test_classification_default(self, browser):
        browser.login().open()
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_classification(dossier)
        self.assertEqual(u'unprotected', value)

    @browsing
    def test_classification_acquired_default(self, browser):
        browser.login().open(self.repofolder)
        self.set_classification(self.repofolder, u'confidential')
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_classification(dossier)
        self.assertEqual(u'confidential', value)

    @browsing
    def test_intermediate_folder_doesnt_break_default_aq(self, browser):
        # An intermediate folderish object that doesn't have the respective
        # field shouldn't break acquisition of the default
        self.set_classification(self.repofolder, u'confidential')

        fti = self.get_fti('opengever.repository.repositoryfolder')
        fti.allowed_content_types = fti.allowed_content_types + ('Dummy',)

        dummy = createContentInContainer(self.repofolder, 'Dummy')
        transaction.commit()
        browser.login().open(dummy)

        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_classification(dossier)
        self.assertEqual(u'confidential', value)


class TestClassificationVocabulary(FunctionalTestCase):

    def setUp(self):
        super(TestClassificationVocabulary, self).setUp()
        self.repofolder = create(Builder('repository'))
        self.field = IClassification['classification']

    def get_classification(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_classification(self, obj, value):
        self.field.set(self.field.interface(obj), value)
        transaction.commit()

    @browsing
    def test_classification_default_choices(self, browser):
        browser.login().open(self.repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        form_field = browser.find('Classification')
        self.assertEqual(
            ['unprotected', 'confidential', 'classified'],
            form_field.options_values)

    @browsing
    def test_aq_value_is_contained_in_choices_if_restricted(self, browser):
        self.set_classification(self.repofolder, u'confidential')

        browser.login().open(self.repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Classification')
        self.assertIn('confidential', form_field.options_values)

    @browsing
    def test_vocab_is_restricted_if_indicated_by_aq_value(self, browser):
        self.set_classification(self.repofolder, u'confidential')

        browser.login().open(self.repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Classification')
        self.assertSetEqual(
            set(['confidential', 'classified']),
            set(form_field.options_values))

    @browsing
    def test_acquired_value_is_suggested_as_default(self, browser):
        self.set_classification(self.repofolder, u'confidential')

        browser.login().open(self.repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Classification')

        self.assertEqual('confidential', form_field.value)
        # Default listed first
        self.assertEqual('confidential', form_field.options_values[0])

    @browsing
    def test_restriction_works_in_edit_form(self, browser):
        self.set_classification(self.repofolder, u'confidential')

        browser.login().open(self.repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        transaction.commit()

        browser.click_on('Edit')
        form_field = browser.find('Classification')
        self.assertSetEqual(
            set(['confidential', 'classified']),
            set(form_field.options_values))


class TestClassificationPropagation(FunctionalTestCase):

    def setUp(self):
        super(TestClassificationPropagation, self).setUp()
        self.repofolder = create(Builder('repository'))
        self.field = IClassification['classification']
        self.grant('Administrator')

    def get_classification(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_classification(self, obj, value):
        self.field.set(self.field.interface(obj), value)
        transaction.commit()

    @browsing
    def test_change_propagates_to_children(self, browser):
        # Start with a loose classification
        self.set_classification(self.repofolder, u'unprotected')

        browser.login().open(self.repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_classification(dossier)
        # Dossier should have inherited classification from repofolder
        self.assertEqual(u'unprotected', value)

        browser.open(self.repofolder, view='edit')
        # Make classification more strict
        browser.fill({'Classification': 'confidential'}).save()
        transaction.commit()

        value = self.get_classification(dossier)
        # Stricter classification should have propagated to dossier
        self.assertEqual(u'confidential', value)

    @browsing
    def test_change_doesnt_propagate_if_old_value_still_valid(self, browser):
        browser.login().open(self.repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({
            'Title': 'My Dossier',
            'Classification': 'confidential'}).save()
        dossier = browser.context

        value = self.get_classification(dossier)
        self.assertEqual(u'confidential', value)

        browser.open(self.repofolder, view='edit')
        browser.fill({'Classification': 'unprotected'}).save()
        transaction.commit()

        value = self.get_classification(dossier)
        self.assertEqual(u'confidential', value)

    @browsing
    def test_propagation_is_depth_limited(self, browser):
        """Propagation of classification is depth limited to 2 levels.
        Not sure why this was implemented this way, but here we test for it.
        """
        # Start with a loose classification
        self.set_classification(self.repofolder, u'unprotected')
        repofolder2 = create(Builder('repository').within(self.repofolder))
        repofolder3 = create(Builder('repository').within(repofolder2))

        browser.login().open(repofolder3)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_classification(dossier)
        # Dossier should have inherited classification from repofolder2
        self.assertEqual(u'unprotected', value)

        browser.open(self.repofolder, view='edit')
        # Make classification more strict on top level repofolder
        browser.fill({'Classification': 'confidential'}).save()
        transaction.commit()

        # Stricter classification should have propagated to repofolder2, but
        # not dossier (because of depth limitation)
        self.assertEqual(u'confidential', self.get_classification(repofolder2))
        self.assertEqual(u'unprotected', self.get_classification(dossier))


class TestPrivacyLayerDefault(FunctionalTestCase):

    def setUp(self):
        super(TestPrivacyLayerDefault, self).setUp()
        self.repofolder = create(Builder('repository'))
        self.field = IClassification['privacy_layer']

    def get_privacy_layer(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_privacy_layer(self, obj, value):
        self.field.set(self.field.interface(obj), value)
        transaction.commit()

    def get_fti(self, portal_type):
        types_tool = api.portal.get_tool('portal_types')
        return types_tool[portal_type]

    @browsing
    def test_privacy_layer_default(self, browser):
        browser.login().open()
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_privacy_layer(dossier)
        self.assertEqual(u'privacy_layer_no', value)

    @browsing
    def test_privacy_layer_acquired_default(self, browser):
        browser.login().open(self.repofolder)
        self.set_privacy_layer(self.repofolder, u'privacy_layer_yes')
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_privacy_layer(dossier)
        self.assertEqual(u'privacy_layer_yes', value)

    @browsing
    def test_intermediate_folder_doesnt_break_default_aq(self, browser):
        # An intermediate folderish object that doesn't have the respective
        # field shouldn't break acquisition of the default
        self.set_privacy_layer(self.repofolder, u'privacy_layer_yes')

        fti = self.get_fti('opengever.repository.repositoryfolder')
        fti.allowed_content_types = fti.allowed_content_types + ('Dummy',)

        dummy = createContentInContainer(self.repofolder, 'Dummy')
        transaction.commit()
        browser.login().open(dummy)

        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_privacy_layer(dossier)
        self.assertEqual(u'privacy_layer_yes', value)


class TestPrivacyLayerVocabulary(FunctionalTestCase):

    def setUp(self):
        super(TestPrivacyLayerVocabulary, self).setUp()
        self.repofolder = create(Builder('repository'))
        self.field = IClassification['privacy_layer']

    def get_privacy_layer(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_privacy_layer(self, obj, value):
        self.field.set(self.field.interface(obj), value)
        transaction.commit()

    @browsing
    def test_privacy_layer_default_choices(self, browser):
        browser.login().open(self.repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        form_field = browser.find('Privacy layer')
        self.assertEqual(
            ['privacy_layer_no', 'privacy_layer_yes'],
            form_field.options_values)

    @browsing
    def test_aq_value_is_contained_in_choices_if_restricted(self, browser):
        self.set_privacy_layer(self.repofolder, u'privacy_layer_yes')

        browser.login().open(self.repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Privacy layer')
        self.assertIn('privacy_layer_yes', form_field.options_values)

    @browsing
    def test_vocab_is_restricted_if_indicated_by_aq_value(self, browser):
        self.set_privacy_layer(self.repofolder, u'privacy_layer_yes')

        browser.login().open(self.repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Privacy layer')
        self.assertSetEqual(
            set(['privacy_layer_yes']),
            set(form_field.options_values))

    @browsing
    def test_acquired_value_is_suggested_as_default(self, browser):
        self.set_privacy_layer(self.repofolder, u'privacy_layer_yes')

        browser.login().open(self.repofolder)
        factoriesmenu.add(u'Business Case Dossier')

        form_field = browser.find('Privacy layer')

        self.assertEqual('privacy_layer_yes', form_field.value)
        # Default listed first
        self.assertEqual('privacy_layer_yes', form_field.options_values[0])

    @browsing
    def test_restriction_works_in_edit_form(self, browser):
        self.set_privacy_layer(self.repofolder, u'privacy_layer_yes')

        browser.login().open(self.repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        transaction.commit()

        browser.click_on('Edit')
        form_field = browser.find('Privacy layer')
        self.assertSetEqual(
            set(['privacy_layer_yes']),
            set(form_field.options_values))


class TestPrivacyLayerPropagation(FunctionalTestCase):

    def setUp(self):
        super(TestPrivacyLayerPropagation, self).setUp()
        self.repofolder = create(Builder('repository'))
        self.field = IClassification['privacy_layer']
        self.grant('Administrator')

    def get_privacy_layer(self, obj):
        return self.field.get(self.field.interface(obj))

    def set_privacy_layer(self, obj, value):
        self.field.set(self.field.interface(obj), value)
        transaction.commit()

    @browsing
    def test_change_propagates_to_children(self, browser):
        # Start with a loose privacy layer
        self.set_privacy_layer(self.repofolder, u'privacy_layer_no')

        browser.login().open(self.repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_privacy_layer(dossier)
        # Dossier should have inherited privacy layer from repofolder
        self.assertEqual(u'privacy_layer_no', value)

        browser.open(self.repofolder, view='edit')
        # Make privacy layer more strict
        browser.fill({'Privacy layer': 'privacy_layer_yes'}).save()
        transaction.commit()

        value = self.get_privacy_layer(dossier)
        # Stricter privacy layer should have propagated to dossier
        self.assertEqual(u'privacy_layer_yes', value)

    @browsing
    def test_change_doesnt_propagate_if_old_value_still_valid(self, browser):
        browser.login().open(self.repofolder)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({
            'Title': 'My Dossier',
            'Privacy layer': 'privacy_layer_yes'}).save()
        dossier = browser.context

        value = self.get_privacy_layer(dossier)
        self.assertEqual(u'privacy_layer_yes', value)

        browser.open(self.repofolder, view='edit')
        browser.fill({'Privacy layer': 'privacy_layer_no'}).save()
        transaction.commit()

        value = self.get_privacy_layer(dossier)
        self.assertEqual(u'privacy_layer_yes', value)

    @browsing
    def test_propagation_is_depth_limited(self, browser):
        """Propagation of privacy layer is depth limited to 2 levels.
        Not sure why this was implemented this way, but here we test for it.
        """
        # Start with a loose privacy layer
        self.set_privacy_layer(self.repofolder, u'privacy_layer_no')
        repofolder2 = create(Builder('repository').within(self.repofolder))
        repofolder3 = create(Builder('repository').within(repofolder2))

        browser.login().open(repofolder3)
        factoriesmenu.add(u'Business Case Dossier')
        browser.fill({'Title': 'My Dossier'}).save()
        dossier = browser.context

        value = self.get_privacy_layer(dossier)
        # Dossier should have inherited privacy layer from repofolder2
        self.assertEqual(u'privacy_layer_no', value)

        browser.open(self.repofolder, view='edit')
        # Reduce privacy layer on top level repofolder
        browser.fill({'Privacy layer': 'privacy_layer_yes'}).save()
        transaction.commit()

        # Reduced privacy layer should have propagated to repofolder2, but
        # not dossier (because of depth limitation)
        self.assertEqual(
            u'privacy_layer_yes', self.get_privacy_layer(repofolder2))
        self.assertEqual(
            u'privacy_layer_no', self.get_privacy_layer(dossier))


class TestClassificationBehavior(FunctionalTestCase):
    use_browser = True

    def setUp(self):
        super(TestClassificationBehavior, self).setUp()

        fti = DexterityFTI('ClassificationFTI',
                           klass="plone.dexterity.content.Container",
                           global_allow=True,
                           filter_content_types=False)
        fti.behaviors = (
            'opengever.base.behaviors.classification.IClassification',)
        self.portal.portal_types._setObject('ClassificationFTI', fti)
        fti.lookupSchema()
        transaction.commit()

    @browsing
    def test_classification_behavior(self, browser):
        # Defaul view doesnt work for system users
        browser.login().open(view='folder_contents')
        self.assertIn('ClassificationFTI', factoriesmenu.addable_types())
        factoriesmenu.add('ClassificationFTI')

        browser.fill({
            'Classification': classification.CLASSIFICATION_CONFIDENTIAL,
            'Privacy layer': classification.PRIVACY_LAYER_YES,
            'Public Trial': classification.PUBLIC_TRIAL_PRIVATE,
            'Public trial statement': u'My statement'
        }).submit()

        self.assertEquals(
            '{0}/classificationfti/view'.format(self.portal.absolute_url()),
            browser.url)

        # Get the created object:
        obj = self.portal.get('classificationfti')
        self.assertNotEquals(None, obj)
        self.assertEquals(classification.CLASSIFICATION_CONFIDENTIAL,
                          obj.classification)
        self.assertEquals(classification.PRIVACY_LAYER_YES, obj.privacy_layer)
        self.assertEquals(classification.PUBLIC_TRIAL_PRIVATE,
                          obj.public_trial)
        self.assertEquals(u'My statement',
                          obj.public_trial_statement)

        # Create a subitem:
        subobj = createContentInContainer(obj,
                                          'ClassificationFTI',
                                          title='testobject')
        transaction.commit()

        browser.open(subobj, view='edit')
        classification_options = browser.css(
            '#form-widgets-IClassification-classification option').text
        self.assertNotIn(classification.CLASSIFICATION_UNPROTECTED,
                         classification_options)
        self.assertIn(classification.CLASSIFICATION_CLASSIFIED,
                      classification_options)

        privacy_options = browser.css(
            '#form-widgets-IClassification-privacy_layer option').text
        self.assertNotIn(classification.PRIVACY_LAYER_NO, privacy_options)

        public_trial_options = browser.css(
            '#form-widgets-IClassification-public_trial option').text
        self.assertEquals(list(classification.PUBLIC_TRIAL_OPTIONS),
                          public_trial_options)

    def test_public_trial_fallback_default_value_is_unchecked(self):
        repo = create(Builder('repository').titled('New repo'))
        self.assertEquals(classification.PUBLIC_TRIAL_UNCHECKED,
                          repo.public_trial)

    def test_public_trial_default_value_is_configurable(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IClassificationSettings)
        expected = classification.PUBLIC_TRIAL_PRIVATE
        settings.public_trial_default_value = expected

        doc = create(Builder('document').titled('My document'))
        self.assertEquals(expected, doc.public_trial)

    def test_public_trial_is_no_longer_restricted_on_subitems(self):
        repo = create(Builder('repository')
                      .titled('New repo')
                      .having(
                          public_trial=classification.PUBLIC_TRIAL_PRIVATE))
        subrepo = create(Builder('repository').titled('New repo').within(repo))

        self.assertEquals(classification.PUBLIC_TRIAL_UNCHECKED,
                          subrepo.public_trial)

    @browsing
    def test_public_trial_is_hidden_on_dossier(self, browser):
        selector = ('#formfield-form-widgets-IClassification-public_trial '
                    '.hidden-widget')
        selector2 = ('#formfield-form-widgets-IClassification-public_trial_'
                     'statement .hidden-widget')

        browser.login().visit(self.portal, view='folder_contents')
        factoriesmenu.add('Business Case Dossier')
        self.assertTrue(browser.css(selector), 'Public trial should be hidden')
        self.assertTrue(browser.css(selector2),
                        'Public trial statement should be hidden')

        dossier = create(Builder('dossier'))
        browser.visit(dossier, view='edit')
        self.assertTrue(browser.css(selector), 'Public trial should be hidden')
        self.assertTrue(browser.css(selector2),
                        'Public trial statement should be hidden')

    @browsing
    def test_public_trial_is_hidden_on_repository(self, browser):
        self.grant('Administrator', 'Contributor', 'Editor', 'Reader')
        selector = ('#formfield-form-widgets-IClassification-public_trial '
                    '.hidden-widget')
        selector2 = ('#formfield-form-widgets-IClassification-public_trial_'
                     'statement .hidden-widget')

        browser.login().visit(self.portal, view='folder_contents')
        factoriesmenu.add('RepositoryFolder')
        self.assertTrue(browser.css(selector), 'Public trial should be hidden')
        self.assertTrue(browser.css(selector2),
                        'Public trial statement should be hidden')

        repository = create(Builder('repository'))
        browser.visit(repository, view='edit')
        self.assertTrue(browser.css(selector), 'Public trial should be hidden')
        self.assertTrue(browser.css(selector2),
                        'Public trial statement should be hidden')


class TestChangesToPublicTrialAreJournalized(FunctionalTestCase):

    def setUp(self):
        super(TestChangesToPublicTrialAreJournalized, self).setUp()

        self.dossier = create(Builder('dossier'))
        self.document = create(Builder('document')
                               .within(self.dossier)
                               .with_dummy_content())

    @browsing
    def test_regular_edit_form_journalizes_changes(self, browser):
        browser.login().open(self.document, view='edit')
        browser.fill({'Public Trial': 'public'}).save()

        journal = JournalHistory(self.document, self.document.REQUEST)
        entry = journal.data()[-1]
        translated_action_title = translate(entry['action']['title'],
                                            context=self.layer['request'])

        self.assertEqual('Public trial changed to "public".',
                         translated_action_title)
        self.assertEquals(TEST_USER_ID, entry['actor'])
        self.assertDictContainsSubset({'type': 'Public trial modified',
                                       'visible': True},
                                      entry['action'])

    @browsing
    def test_public_trial_edit_form_journalizes_changes(self, browser):
        browser.login().open(self.document, view='edit_public_trial')
        browser.fill({'Public Trial': 'public'}).save()

        journal = JournalHistory(self.document, self.document.REQUEST)
        entry = journal.data()[-1]
        translated_action_title = translate(entry['action']['title'],
                                            context=self.layer['request'])

        self.assertEqual('Public trial changed to "public".',
                         translated_action_title)
        self.assertEquals(TEST_USER_ID, entry['actor'])
        self.assertDictContainsSubset({'type': 'Public trial modified',
                                       'visible': True},
                                      entry['action'])
