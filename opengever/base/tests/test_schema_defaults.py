from opengever.base.tests.sample_behavior.sample import ISampleSchema
from opengever.testing import IntegrationTestCase
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.fti import register
from plone.dexterity.utils import createContentInContainer
from Products.CMFCore.utils import getToolByName


class TestSchemaLevelDefaultsForBehaviors(IntegrationTestCase):

    def setUp(self):
        super(TestSchemaLevelDefaultsForBehaviors, self).setUp()

        fti = DexterityFTI('SampleItem')
        fti.klass = 'plone.dexterity.content.Item'
        fti.behaviors = ('opengever.base.tests.sample_behavior.sample.ISampleSchema', )
        fti.schema = 'opengever.base.tests.emptyschema.IEmptySchema'

        typestool = getToolByName(self.portal, 'portal_types')
        typestool._setObject('SampleItem', fti)
        register(fti)

        site_fti = typestool['Plone Site']
        site_fti.allowed_content_types = site_fti.allowed_content_types + ('SampleItem', )

    def test_defaults_on_behavior_schemata_take_effect(self):
        self.login(self.manager)

        obj = createContentInContainer(self.portal, 'SampleItem')
        obj = ISampleSchema(obj)
        self.assertEquals(ISampleSchema['foobar'].default, obj.foobar)
