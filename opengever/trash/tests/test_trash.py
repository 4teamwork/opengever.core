from Products.CMFCore.utils import getToolByName
from opengever.core.testing import OPENGEVER_FUNCTIONAL_TESTING
from opengever.trash.testing import OPENGEVER_TRASH_INTEGRATION_TESTING
from opengever.trash.trash import ITrashable, ITrashed
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import setRoles
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.utils import createContentInContainer
from plone.testing.z2 import Browser
from zope.component import getUtility
import transaction
import unittest2 as unittest

class TestTrash(unittest.TestCase):

    layer = OPENGEVER_TRASH_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer.get('app')
        self.portal = self.layer.get('portal')
        self.request = self.layer.get('request')

    def test_trash(self):
        fti = DexterityFTI('TrashTestFTI',
                           klass="plone.dexterity.content.Container",
                           global_allow=True,
                           filter_content_types=False)
        fti.behaviors = ('plone.app.content.interfaces.INameFromTitle', 'opengever.trash.trash.ITrashable')
        self.portal.portal_types._setObject('TrashTestFTI', fti)
        # schema = fti.lookupSchema()

        utem1 = createContentInContainer(self.portal, 'TrashTestFTI',
                                         checkConstraints=False,
                                         title=u'\xfctem1', checked_out=False)

        self.portal.REQUEST['paths'] = ['/'.join(utem1.getPhysicalPath())]
        self.assertEquals('http://nohost/plone/utem1#trash',
                          utem1.restrictedTraverse('trashed')())
        self.assertTrue(ITrashed.providedBy(utem1),
                        "The item %s should be trashed" % utem1)

        trashed_items = self.portal.portal_catalog(portal_type="TrashTestFTI",
                                                   trashed=True)
        self.assertEquals(1, len(trashed_items))

        self.portal.REQUEST['paths'] = ['/'.join(utem1.getPhysicalPath())]
        self.assertEquals('http://nohost/plone/utem1#documents',
                          utem1.restrictedTraverse('trashed')())

        self.portal.REQUEST['paths'] = ['/'.join(utem1.getPhysicalPath())]
        self.assertEquals('http://nohost/plone/utem1#documents',
                          utem1.restrictedTraverse('untrashed')())

        self.assertEquals([], list(self.portal.portal_catalog(portal_type="TrashTestFTI", trashed=True)))
