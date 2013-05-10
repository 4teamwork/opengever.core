from opengever.testing import FunctionalTestCase
from plone.dexterity.fti import DexterityFTI
from opengever.base.interfaces import IReferenceNumberPrefix

class TestReferenceAdapter(FunctionalTestCase):

    def setUp(self):
        super(TestReferenceAdapter, self).setUp()
        self.grant('Contributor')
        fti = DexterityFTI('OpenGeverBaseFTI3', klass="plone.dexterity.content.Container",
                           global_allow=True,
                           allowed_content_types=['OpenGeverBaseFTI3'],
                           behaviors=["opengever.base.interfaces.IReferenceNumberPrefix"])
        self.portal.portal_types._setObject('OpenGeverBaseFTI3', fti)

    def test_reference_adapter(self):
        # Do some imports, and standard configuration:
        self.portal.invokeFactory('OpenGeverBaseFTI3', 'f1')

        # Create Folder, and items and get the referenceNumberPrefixAdapter:
        f1 = self.portal.get('f1')
        adapter = IReferenceNumberPrefix(f1)
        f1.invokeFactory('OpenGeverBaseFTI3', 'Item1')
        item1 = f1.get('Item1')
        f1.invokeFactory('OpenGeverBaseFTI3', 'Item2')
        item2 = f1.get('Item2')

        # Check the numbering concept, starting by 1:
        # (get_next_number() should always return unicode!)
        self.assertEquals(u'1', adapter.get_next_number())
        
        item1 = f1.get('Item1')
        self.assertEquals(u'1', adapter.set_number(item1))
        self.assertEquals(u'1', adapter.get_number(item1))
        self.assertEquals(u'2', adapter.get_next_number())

        # The next number generator should be able to increase number greater than 9:
        # It also give allways the next number from the highest one, and not use all numbers
        self.assertEquals(u'9', adapter.set_number(item2, u'9'))
        self.assertEquals(u'10', adapter.get_next_number())

        # and also alpha-numeric numbers:
        self.assertEquals(u'A1A15', adapter.set_number(item1, u'A1A15'))
        self.assertEquals(u'A1A16', adapter.set_number(item2))
        self.assertEquals(u'A1A17', adapter.get_next_number())
        

        # Check the is_valid_number() method:
        self.assertFalse(adapter.is_valid_number(u'A1A16'))
        self.assertTrue(adapter.is_valid_number(u'A1A17'))
