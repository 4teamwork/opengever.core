from Products.CMFPlone.interfaces import IPloneSiteRoot
from ftw.testing import MockTestCase
from grokcore.component.testing import grok
from opengever.base.interfaces import IUniqueNumberGenerator
from opengever.base.interfaces import IUniqueNumberUtility
from zope.annotation.interfaces import IAnnotations
from zope.component import getAdapter
from zope.component import getUtility
from zope.interface import Interface, directlyProvides

class TestUniqueNumberGenerator(MockTestCase):

    def setUp(self):
        super(TestUniqueNumberGenerator, self).setUp()
        grok('opengever.base.unique_number')

    def test_genrator(self):
        # portal
        portal = self.create_dummy()
        directlyProvides(portal, IPloneSiteRoot)

        # setup annotations
        annotation_factory = self.mocker.mock()
        self.mock_adapter(annotation_factory, IAnnotations, (Interface,))
        self.expect(annotation_factory(portal)).result({})

        self.replay()

        adapter = getAdapter(portal, IUniqueNumberGenerator)
        self.assertEquals(
            adapter.generate('test.portal.type-2011'), 1)
        self.assertEquals(
            adapter.generate('second.test.portal.type-2012'), 1)
        self.assertEquals(
            adapter.generate('test.portal.type-2012'), 1)
        self.assertEquals(
            adapter.generate('test.portal.type-2011'), 2)
        self.assertEquals(
            adapter.generate('second.test.portal.type-2012'), 2)

    def test_utility(self):
        # portal
        portal = self.create_dummy()
        directlyProvides(portal, IPloneSiteRoot)

        portal_url_tool = self.stub()
        self.mock_tool(portal_url_tool, 'portal_url')
        self.expect(
            portal_url_tool.getPortalObject()).result(portal)

        # setup annotations
        annotation_factory = self.mocker.mock()
        self.mock_adapter(annotation_factory, IAnnotations, (Interface,))
        self.expect(annotation_factory(portal)).result({}).count(1, None)

        # mocking context
        obj = self.mocker.mock()
        self.expect(annotation_factory(obj)).result({}).count(1, None)
        self.expect(obj.portal_type).result('test_portal_type').count(0, None)
        self.expect(obj.getPortalObject()).result(portal).count(0, None)

        obj2 = self.mocker.mock()
        self.expect(annotation_factory(obj2)).result({}).count(1, None)
        self.expect(obj2.portal_type).result('test_portal_type').count(0, None)
        self.expect(obj2.getPortalObject()).result(portal).count(0, None)

        self.expect(obj.portal_type).result('test_portal_type').count(0, None)
        self.replay()

        # utility
        utility = getUtility(IUniqueNumberUtility)

        # first object
        self.assertEquals(utility.get_number(obj, year='2011'), 1)
        self.assertEquals(utility.get_number(obj, year='2012'), 1)
        self.assertEquals(utility.get_number(obj, year='2011'), 1)

        # second object
        self.assertEquals(utility.get_number(obj2, year='2011'), 2)
        self.assertEquals(utility.get_number(obj2, year='2012'), 2)
        self.assertEquals(utility.get_number(obj2, year='2011'), 2)
        self.assertEquals(utility.get_number(obj2, foo='2011'), 1)

        # same values doesn't made problems
        self.assertEquals(utility.get_number(obj, foo='foo', bar='bar'), 1)
        self.assertEquals(utility.get_number(obj2, foo='foo', bar='bar'), 2)
        self.assertEquals(utility.get_number(obj2, foo='foo', baz='bar'), 1)
        self.assertEquals(utility.get_number(obj, foo='foo', baz='bar'), 2)

        self.assertEquals(utility.get_number(obj2, month=('2011', 5)), 1)
        self.assertEquals(utility.get_number(obj2, month=('2011', 5)), 1)

        #removing should also work, but the removed number is not recyclable
        utility.remove_number(obj2, year='2011')
        self.assertEquals(utility.get_number(obj2, year='2011'), 3)
