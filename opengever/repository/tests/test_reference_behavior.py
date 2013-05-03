from opengever.core.testing import OPENGEVER_FUNCTIONAL_TESTING
from opengever.repository.behaviors import referenceprefix
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.schema import SCHEMA_CACHE
from plone.testing.z2 import Browser
from z3c.form.interfaces import IValidator
from zope.component import getMultiAdapter, provideAdapter
from zope.component import provideUtility
import transaction
import unittest2 as unittest


class TestReferenceBehavior(unittest.TestCase):
    """
    The reference number Behavior show a integer field (reference Number), the reference number field.
    The behavior set the default value to the next possible sequence number:
    """

    layer=OPENGEVER_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']
        self.request = self.layer['request']

        setRoles(self.portal, TEST_USER_ID, ['Contributor'])


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

        #If we access the site as an admin TTW::
        browser = Browser(self.app)
        browser.handleErrors = False
        browser.addHeader('Authorization', 'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD))

        #We can see this type in the addable types at the root of the site::
        browser.open('http://nohost/plone/folder_factories')
        self.assertIn('ReferenceFTI', browser.contents)
        browser.getControl('ReferenceFTI').click()
        browser.getControl('Add').click()
        self.assertEquals('http://nohost/plone/++add++ReferenceFTI', browser.url)
        self.assertIn('reference_number_prefix', browser.contents)
        self.assertEquals("1",
                          browser.getControl(name='form.widgets.IReferenceNumberPrefix.reference_number_prefix').value)
        browser.getControl('Title').value = 'Hugo'
        browser.getControl('Save').click()
        self.assertEquals('http://nohost/plone/referencefti/view', browser.url)

        #checked the saved obj ::
        obj = self.portal.get('referencefti')
        self.assertTrue(referenceprefix.IReferenceNumberPrefixMarker.providedBy(obj))

        #Add a second Type in this folder::
        browser.open('http://nohost/plone/folder_factories')
        self.assertIn('ReferenceFTI', browser.contents)
        browser.getControl('ReferenceFTI').click()
        browser.getControl('Add').click()
        self.assertEquals('http://nohost/plone/++add++ReferenceFTI', browser.url)
        self.assertIn('reference_number_prefix', browser.contents)
        browser.getControl('Title').value = 'Hans'
        self.assertEquals("2", browser.getControl('Reference Prefix').value)

        #We should not be able to use a already used value::
        browser.getControl('Reference Prefix').value = '1'
        browser.getControl('Save').click()
        self.assertEquals('http://nohost/plone/++add++ReferenceFTI', browser.url)

        #Ok, lets use a free one::
        browser.getControl('Reference Prefix').value = '2'
        browser.getControl('Save').click()
        self.assertEquals('http://nohost/plone/referencefti-1/view', browser.url)

        #It should be possbile to use alpha-numeric references::
        browser.open('http://nohost/plone/++add++ReferenceFTI')
        self.assertEquals('3', browser.getControl('Reference Prefix').value)

        browser.getControl('Reference Prefix').value = 'a1x10'
        browser.getControl('Title').value = 'Peter'
        browser.getControl('Save').click()
        self.assertEquals('http://nohost/plone/referencefti-2/view', browser.url)

        #Check the reference numbers of the objects::
        data = []
        for obj in self.portal.objectValues():
            if referenceprefix.IReferenceNumberPrefixMarker.providedBy(obj):
                num = referenceprefix.IReferenceNumberPrefix(obj).reference_number_prefix
                data.append((obj.Title(), num))
        self.assertEquals([('Hugo', u'1'),
                           ('Hans', u'2'),
                           ('Peter', u'a1x10')], data)
