from opengever.core.testing import OPENGEVER_INTEGRATION_TESTING
from opengever.trash.trash import ITrashed
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.utils import createContentInContainer
import unittest2 as unittest

class TestTrash(unittest.TestCase):

    layer = OPENGEVER_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer.get('app')
        self.portal = self.layer.get('portal')
        setRoles(self.portal, TEST_USER_ID, ['Member', 'Contributor', 'Manager'])

        fti = DexterityFTI('TrashTestFTI',
                           klass="plone.dexterity.content.Container",
                           global_allow=True,
                           filter_content_types=False)
        fti.behaviors = ('plone.app.content.interfaces.INameFromTitle',
                         'opengever.trash.trash.ITrashable')
        self.portal.portal_types._setObject('TrashTestFTI', fti)

    def restore_item(self, item):
        self.portal.REQUEST['paths'] = ['/'.join(item.getPhysicalPath())]
        current_url = item.restrictedTraverse('untrashed')()
        self.assertFalse(ITrashed.providedBy(item),
                        "The item %s should not be trashed" % item)
        return current_url

    def test_trashing_items(self):
        item = self.create_item("item")
        unicode_item = self.create_item(u'\xfctem')

        self.assertEquals('http://nohost/plone/item#trash',
                          self.trash_item(item))
        self.assert_trashed_item_count(1)

        self.assertEquals('http://nohost/plone/utem#trash',
                          self.trash_item(unicode_item))
        self.assert_trashed_item_count(2)

    def test_trashing_trashed_items_will_result_in_the_fallback(self):
        item = self.create_item("item")
        self.trash_item(item)
        url = self.trash_item(item)
        self.assertEquals("http://nohost/plone/item#documents", url)

    def test_restoring_items(self):
        item = self.create_item("anotheritem")
        self.trash_item(item)
        self.assert_trashed_item_count(1)

        url = self.restore_item(item)
        self.assertEquals('http://nohost/plone/anotheritem#documents', url)
        self.assert_trashed_item_count(0)

    def assert_trashed_item_count(self, count):
        trashed_items = list(self.portal.portal_catalog(portal_type="TrashTestFTI",
                                                        trashed=True))
        self.assertEquals(count, len(trashed_items))

    def create_item(self, title):
        return createContentInContainer(self.portal, 'TrashTestFTI',
                                        checkConstraints=False,
                                        title=title, checked_out=False)

    def trash_item(self, item):
        self.portal.REQUEST['paths'] = ['/'.join(item.getPhysicalPath())]
        current_url = item.restrictedTraverse('trashed')()
        self.assertTrue(ITrashed.providedBy(item),
                "The item %s should be trashed" % item)
        return current_url
