from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from opengever.base.behaviors import classification
from opengever.base.behaviors.classification import IClassificationSettings
from opengever.journal.browser import JournalHistory
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.utils import createContentInContainer
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.i18n import translate
import transaction


class TestClassificationBehavior(FunctionalTestCase):
    use_browser = True

    def setUp(self):
        super(TestClassificationBehavior, self).setUp()
        self.grant('Contributor')

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
            'Title': u'My Object',
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
        self.grant('Manager')
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
        self.grant('Contributor')

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
