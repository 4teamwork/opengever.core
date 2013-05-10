from opengever.base.behaviors import classification
from opengever.testing import FunctionalTestCase
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.utils import createContentInContainer
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
        fti.behaviors = ('opengever.base.behaviors.classification.IClassification',)
        self.portal.portal_types._setObject('ClassificationFTI', fti)
        fti.lookupSchema()
        transaction.commit()

    def test_classification_behavior(self):
        # We can see this type in the addable types at the root of the site:
        self.browser.open("http://nohost/plone/folder_factories")
        self.assertPageContains('ClassificationFTI')

        self.browser.getControl("ClassificationFTI").click()
        self.browser.getControl("Add").click()
        self.browser.getControl(name="form.widgets.title").value = "My Object"
        self.browser.getControl(name="form.widgets.IClassification.classification:list").value = [classification.CLASSIFICATION_CONFIDENTIAL]
        self.browser.getControl(name="form.widgets.IClassification.privacy_layer:list").value = [classification.PRIVACY_LAYER_YES]
        self.browser.getControl(name="form.widgets.IClassification.public_trial:list").value = [classification.PUBLIC_TRIAL_PRIVATE]
        self.browser.getControl(name="form.widgets.IClassification.public_trial_statement").value = 'My Statement'
        self.browser.getControl(name="form.buttons.save").click()
        self.assertCurrentUrl('http://nohost/plone/classificationfti/view')

        # Get the created object:
        obj = self.portal.get('classificationfti')
        self.assertNotEquals(None, obj)

        # Check the values of the created object:
        self.assertEquals(classification.CLASSIFICATION_CONFIDENTIAL, obj.classification)
        self.assertEquals(classification.PRIVACY_LAYER_YES, obj.privacy_layer)
        self.assertEquals(classification.PUBLIC_TRIAL_PRIVATE, obj.public_trial)
        self.assertEquals('My Statement', obj.public_trial_statement)

        # Create a subitem:
        createContentInContainer(obj, 'ClassificationFTI', title='testobject')
        transaction.commit()

        self.browser.open('http://nohost/plone/classificationfti/classificationfti/edit')
        class_cont = self.browser.getControl(name="form.widgets.IClassification.classification:list")
        self.assertNotIn(classification.CLASSIFICATION_UNPROTECTED, class_cont.options)
        self.assertIn(classification.CLASSIFICATION_CLASSIFIED, class_cont.options)
        class_cont = self.browser.getControl(name="form.widgets.IClassification.privacy_layer:list")
        self.assertNotIn(classification.PRIVACY_LAYER_NO, class_cont.options)
        class_cont = self.browser.getControl(name="form.widgets.IClassification.public_trial:list")
        self.assertNotIn(classification.PUBLIC_TRIAL_PUBLIC, class_cont.options)
