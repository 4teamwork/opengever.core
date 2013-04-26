from Products.CMFCore.utils import getToolByName
from datetime import datetime
from opengever.ogds.base.interfaces import IClientConfiguration
from opengever.task.testing import OPENGEVER_TASK_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.app.testing import setRoles, login
from plone.dexterity.utils import createContentInContainer
from plone.memoize.interfaces import ICacheChooser
from plone.registry.interfaces import IRegistry
from z3c.relationfield.relation import RelationValue
from zope.component import getUtility, queryUtility
from zope.event import notify
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectModifiedEvent
import unittest2 as unittest


def obj2brain(obj):
    catalog = getToolByName(obj, 'portal_catalog')
    query = {'path': {'query': '/'.join(obj.getPhysicalPath()),
                  'depth': 0}}
    brains = catalog(query)
    if len(brains) == 0:
        raise Exception('Not in catalog: %s' % obj)
    else:
        return brains[0]


def getindexDataForObj(obj):
    catalog = getToolByName(obj, 'portal_catalog')
    return catalog.getIndexDataForRID(obj2brain(obj).getRID())


class TestTaskIndexers(unittest.TestCase):

    layer = OPENGEVER_TASK_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal.portal_types['opengever.task.task'].global_allow = True

        setRoles(
            self.portal, TEST_USER_ID, ['Contributor', 'Editor', 'Manager'])
        login(self.portal, TEST_USER_NAME)

        self.task = createContentInContainer(
            self.portal, 'opengever.task.task', checkConstraints=False,
            title="Test task 1")

        self.subtask = createContentInContainer(
            self.task, 'opengever.task.task', checkConstraints=False,
            title="Test task 1")

        self.doc1 = createContentInContainer(
            self.portal, 'opengever.document.document',
            checkConstraints=False, title=u"Doc One")

        self.doc2 = createContentInContainer(
            self.portal, 'opengever.document.document',
            checkConstraints=False, title=u"Doc Two")

    def test_date_of_completion(self):
        self.assertEquals(
            obj2brain(self.task).date_of_completion,
            datetime(1970, 1, 1))

        self.task.date_of_completion = datetime(2012, 2, 2)
        self.task.reindexObject()

        self.assertEquals(
            obj2brain(self.task).date_of_completion,
            datetime(2012, 2, 2))

    def test_assigned_client(self):

        self.assertEquals(
            obj2brain(self.task).assigned_client, '')

        self.task.responsible = 'hugo.boss'
        self.task.responsible_client = 'client_xy'
        self.task.reindexObject()

        self.assertEquals(
            obj2brain(self.task).assigned_client, 'client_xy')

    def test_client_id(self):

        self.assertEquals(obj2brain(self.task).client_id, u'plone')

        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IClientConfiguration)
        proxy.client_id = u'client_xy'

        # invalidate caches
        cache = queryUtility(ICacheChooser)(
            'opengever.ogds.base.utils.get_client_id')
        cache.ramcache.invalidateAll()
        self.task.reindexObject()

        self.assertEquals(
            obj2brain(self.task).client_id, u'client_xy')

    def test_is_subtask(self):

        self.assertFalse(obj2brain(self.task).is_subtask)

        self.assertTrue(obj2brain(self.subtask).is_subtask)

    def test_related_items(self):

        intids = getUtility(IIntIds)

        # no relation
        self.assertEquals(
            getindexDataForObj(self.task).get('related_items'), '')

        self.task.relatedItems = [RelationValue(intids.getId(self.doc1))]
        notify(ObjectModifiedEvent(self.task))
        self.task.reindexObject()

        self.assertEquals(
            getindexDataForObj(self.task).get('related_items'),
            [intids.getId(self.doc1)])

        # multiple relations
        self.task.relatedItems = [
            RelationValue(intids.getId(self.doc2)),
            RelationValue(intids.getId(self.doc1))]

        notify(ObjectModifiedEvent(self.task))
        self.task.reindexObject()

        self.assertEquals(
            getindexDataForObj(self.task).get('related_items'),
            [intids.getId(self.doc1), intids.getId(self.doc2)])

    def test_searchable_text(self):
        self.task.title = u'Test Aufgabe'
        self.task.text = u'Lorem ipsum olor sit amet'
        self.task.responsible = TEST_USER_ID

        self.task.reindexObject()

        self.assertEquals(
            getindexDataForObj(self.task).get('SearchableText'),
            ['test', 'aufgabe', 'lorem', 'ipsum', 'olor', 'sit',
             'amet', '1', 'user', 'test', 'test_user_1_'])

