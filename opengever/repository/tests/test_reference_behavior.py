from opengever.repository.behaviors import referenceprefix
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.schema import SCHEMA_CACHE
from z3c.form.interfaces import IValidator
from zope.component import getMultiAdapter, provideAdapter
from zope.component import provideUtility
from opengever.testing import FunctionalTestCase
import transaction


class TestReferenceBehavior(FunctionalTestCase):
    """
    The reference number Behavior show a integer field (reference Number), the reference number field.
    The behavior set the default value to the next possible sequence number:
    """
    use_browser = True

    def setUp(self):
        super(TestReferenceBehavior, self).setUp()
        self.grant('Contributor')

    def test_reference_behavior(self):
        # Since plone tests sucks, we need to re-register the reference number validator again -.-
        getMultiAdapter((self.portal, None, None, referenceprefix.IReferenceNumberPrefix['reference_number_prefix'], None), IValidator)
        provideAdapter(referenceprefix.ReferenceNumberPrefixValidator)
        getMultiAdapter((self.portal, None, None, referenceprefix.IReferenceNumberPrefix['reference_number_prefix'], None), IValidator)

        #When we create a dexterity content type::
        fti = DexterityFTI('ReferenceFTI')
        fti.behaviors = ('opengever.repository.behaviors.referenceprefix.IReferenceNumberPrefix',)
        self.portal.portal_types._setObject('ReferenceFTI', fti)
        provideUtility(fti, IDexterityFTI, name=u'ReferenceFTI')
        SCHEMA_CACHE.clear()
        fti.lookupSchema()
        transaction.commit()

        #We can see this type in the addable types at the root of the site::
        self.browser.open('http://nohost/plone/folder_factories')
        self.assertPageContains('ReferenceFTI')
        self.browser.getControl('ReferenceFTI').click()
        self.browser.getControl('Add').click()
        self.browser.assert_url('http://nohost/plone/++add++ReferenceFTI')
        self.assertPageContains('reference_number_prefix')
        self.assertEquals("1", self.browser.getControl(name='form.widgets.IReferenceNumberPrefix.reference_number_prefix').value)
        self.browser.getControl('Title').value = 'Hugo'
        self.browser.getControl('Save').click()
        self.browser.assert_url('http://nohost/plone/referencefti/view')

        #checked the saved obj ::
        obj = self.portal.get('referencefti')
        self.assertTrue(referenceprefix.IReferenceNumberPrefixMarker.providedBy(obj))

        #Add a second Type in this folder::
        self.browser.open('http://nohost/plone/folder_factories')
        self.assertPageContains('ReferenceFTI')
        self.browser.getControl('ReferenceFTI').click()
        self.browser.getControl('Add').click()
        self.browser.assert_url('http://nohost/plone/++add++ReferenceFTI')
        self.assertPageContains('reference_number_prefix')
        self.browser.getControl('Title').value = 'Hans'
        self.assertEquals("2", self.browser.getControl('Reference Prefix').value)

        #We should not be able to use a already used value::
        self.browser.getControl('Reference Prefix').value = '1'
        self.browser.getControl('Save').click()
        self.browser.assert_url('http://nohost/plone/++add++ReferenceFTI')

        #Ok, lets use a free one::
        self.browser.getControl('Reference Prefix').value = '2'
        self.browser.getControl('Save').click()
        self.browser.assert_url('http://nohost/plone/referencefti-1/view')

        #It should be possbile to use alpha-numeric references::
        self.browser.open('http://nohost/plone/++add++ReferenceFTI')
        self.assertEquals('3', self.browser.getControl('Reference Prefix').value)

        self.browser.getControl('Reference Prefix').value = 'a1x10'
        self.browser.getControl('Title').value = 'Peter'
        self.browser.getControl('Save').click()
        self.browser.assert_url('http://nohost/plone/referencefti-2/view')

        #Check the reference numbers of the objects::
        data = []
        for obj in self.portal.objectValues():
            if referenceprefix.IReferenceNumberPrefixMarker.providedBy(obj):
                num = referenceprefix.IReferenceNumberPrefix(obj).reference_number_prefix
                data.append((obj.Title(), num))
        self.assertEquals([('Hugo', u'1'),
                           ('Hans', u'2'),
                           ('Peter', u'a1x10')], data)
