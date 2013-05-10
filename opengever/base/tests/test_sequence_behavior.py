from opengever.base.interfaces import ISequenceNumber
from opengever.testing import FunctionalTestCase
from plone.dexterity.fti import DexterityFTI
from zope.component import getUtility

class TestSequenceBehavior(FunctionalTestCase):
    use_browser = True

    def setUp(self):
        super(TestSequenceBehavior, self).setUp()
        self.grant('Manager')

        fti = DexterityFTI('type1', klass="plone.dexterity.content.Container", global_allow=True, allowed_content_types=['type1'], behaviors=["opengever.base.behaviors.sequence.ISequenceNumberBehavior"])
        self.portal.portal_types._setObject('type1', fti)
        fti = DexterityFTI('type2', klass="plone.dexterity.content.Container", global_allow=True, allowed_content_types=['type2'])
        self.portal.portal_types._setObject('type2', fti)
        self.portal.invokeFactory('type1', 'n1')
        self.portal.invokeFactory('type1', 'n2')
        self.portal.invokeFactory('type2', 'f1')

    def test_sequence_behavior(self):
        seq_utility = getUtility(ISequenceNumber)
        n1 = self.portal.get('n1')
        self.assertEquals(1, seq_utility.get_number(n1))

        n2 = self.portal.get('n2')
        self.assertEquals(2, seq_utility.get_number(n2))

        self.assertEquals(1, seq_utility.get_number(n1))

        # the sequence number isn't recyclable
        self.portal.manage_delObjects('n2')
        self.portal.invokeFactory('type1', 'n3')
        self.assertEquals(3, seq_utility.get_number(self.portal.get('n3')))

        # and also the a copy should become a new number
        cb = self.portal.manage_copyObjects('n1')
        self.portal.manage_pasteObjects(cb)
        self.assertEquals(4, seq_utility.get_number(self.portal.get('copy_of_n1')))

        # the folder numbering should be start now also by 1
        f1 = self.portal.get('f1')
        self.assertEquals(1, seq_utility.get_number(f1))
