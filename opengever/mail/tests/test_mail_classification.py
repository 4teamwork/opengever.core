from ftw.builder import Builder
from ftw.builder import create
from opengever.base.behaviors.classification import CLASSIFICATION_UNPROTECTED
from opengever.base.behaviors.classification import IClassificationMarker
from opengever.base.behaviors.classification import IClassificationSettings
from opengever.base.behaviors.classification import PRIVACY_LAYER_NO
from opengever.base.behaviors.classification import PUBLIC_TRIAL_PRIVATE
from opengever.base.behaviors.classification import PUBLIC_TRIAL_UNCHECKED
from opengever.testing import FunctionalTestCase
from pkg_resources import resource_string
from plone.dexterity.interfaces import IDexterityFTI
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


MAIL_DATA = resource_string('opengever.mail.tests', 'mail.txt')


class TestMailMetadata(FunctionalTestCase):
    use_browser = True

    def setUp(self):
        super(TestMailMetadata, self).setUp()
        self.grant('Contributor', 'Editor', 'Member', 'Manager')

    def test_fill_classification_infos_of_new_mail(self):
        mail = create(Builder("mail").with_message(MAIL_DATA))

        self.assertEquals(mail.classification, CLASSIFICATION_UNPROTECTED)
        self.assertEquals(mail.privacy_layer, PRIVACY_LAYER_NO)
        self.assertEquals(mail.public_trial, PUBLIC_TRIAL_UNCHECKED)

        # XXX: imho this should be a empty string, not None, since the field
        # has a default value (empty string)
        self.assertIsNone(mail.public_trial_statement)

    def test_public_trial_default_is_configurable(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IClassificationSettings)
        expected = PUBLIC_TRIAL_PRIVATE
        settings.public_trial_default_value = expected
        mail = create(Builder("mail").with_message(MAIL_DATA))
        self.assertEquals(mail.public_trial, PUBLIC_TRIAL_PRIVATE)

    def test_classification_initialization_upgrade_step(self):
        fti = getUtility(IDexterityFTI, name=u'ftw.mail.mail')
        behaviors = list(fti.behaviors)
        behaviors.remove(
            u'opengever.base.behaviors.classification.IClassification')
        fti._updateProperty('behaviors', tuple(behaviors))

        mail = create(Builder("mail").with_message(MAIL_DATA))

        from opengever.mail.upgrades.to3402 import AddClassifiactionBehavior
        AddClassifiactionBehavior(self.portal.portal_setup)

        assert IClassificationMarker.providedBy(mail)

        self.assertEquals(mail.classification, CLASSIFICATION_UNPROTECTED)
        self.assertEquals(mail.privacy_layer, PRIVACY_LAYER_NO)
        self.assertEquals(mail.public_trial, PUBLIC_TRIAL_UNCHECKED)
        self.assertEquals(mail.public_trial_statement, u'')

    def test_mail_public_trial_in_catalog_metadata(self):
        create(Builder("mail").with_message(MAIL_DATA))
        brain = self.portal.portal_catalog(portal_type='ftw.mail.mail')[0]
        self.assertEquals(brain.public_trial, PUBLIC_TRIAL_UNCHECKED)
