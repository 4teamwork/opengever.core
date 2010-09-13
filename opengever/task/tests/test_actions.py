import unittest
from Products.PloneTestCase.ptc import PloneTestCase
from zope.component.interfaces import IObjectEvent
from zope.interface import implements
from zope.component import getUtility, getMultiAdapter
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleAction
from plone.contentrules.rule.interfaces import IExecutable
from plone.app.contentrules.rule import Rule
from opengever.task.tests.layer import Layer
from AccessControl import getSecurityManager
from zope.app.intid.interfaces import IIntIds
from z3c.relationfield import RelationValue

from opengever.task.actions.addlocalroles import AddLocalRolesAction, AddLocalRolesEditForm

class DummyEvent(object):
    implements(IObjectEvent)
    
    def __init__(self, object):
        self.object = object

class TestAddLocalRolesAction(PloneTestCase):
    
    layer = Layer

    def afterSetUp(self):
        self.setRoles(('Manager',))
        #self.folder.invokeFactory('Folder', 'f1')
        #self.folder.f1.invokeFactory('Document', 'd1')
        #self.folder.invokeFactory('opengever.task.task', 't1')
        #self.folder.t1.setRelatedItems(self.folder.f1.d2)

    def testRegistered(self): 
        element = getUtility(IRuleAction, name='opengever.task.actions.AddLocalRoles')
        self.assertEquals('opengever.task.actions.AddLocalRoles', element.addview)
        self.assertEquals('edit', element.editview)
        self.assertEquals(None, element.for_)
        self.assertEquals(IObjectEvent, element.event)

    def testInvokeAddView(self): 
        element = getUtility(IRuleAction, name='opengever.task.actions.AddLocalRoles')
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')
        
        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+action')
        addview = getMultiAdapter((adding, self.portal.REQUEST), name=element.addview)
        
        addview.createAndAdd(data={
            'object_roles': set(['Reader']),
            'related_items_roles': set(['Reader']),
            'parent_roles': set(['Contributor']),
        })
        
        e = rule.actions[0]
        self.failUnless(isinstance(e, AddLocalRolesAction))
        self.assertEquals(set(['Reader']), e.object_roles)
        self.assertEquals(set(['Reader']), e.related_items_roles)
        self.assertEquals(set(['Contributor']), e.parent_roles)
    
    def testInvokeEditView(self): 
        element = getUtility(IRuleAction, name='opengever.task.actions.AddLocalRoles')
        e = AddLocalRolesAction()
        editview = getMultiAdapter((e, self.folder.REQUEST), name=element.editview)
        self.failUnless(isinstance(editview, AddLocalRolesEditForm))
    
    def testExecute(self):
        self.folder.invokeFactory('opengever.task.task', 'task-1')
        self.folder.get('task-1').responsible = 'testuser'
        e = AddLocalRolesAction()
        e.object_roles = set(['Reader'])
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.get('task-1'))), IExecutable)
        self.assertEquals(True, ex())
        local_roles = dict(self.folder.get('task-1').get_local_roles())
        self.assertEquals(('Reader',), local_roles.get('testuser'))
        
    def test_related_items_roles(self):
        self.folder.invokeFactory('opengever.task.task', 'task-1')
        self.folder.get('task-1').responsible = 'testuser'
        e = AddLocalRolesAction()
        e.related_items_roles = set(['Reader'])
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.get('task-1'))), IExecutable)
        # test with no related items
        self.assertEquals(True, ex())
        # add a related item
        self.folder.invokeFactory('Document', 'document-1')
        intids = getUtility(IIntIds)
        self.folder.get('task-1').relatedItems = [RelationValue(intids.getId(self.folder.get('document-1'))),]
        ex()
        local_roles = dict(self.folder.get('document-1').get_local_roles())
        self.assertEquals(('Reader',), local_roles.get('testuser'))        
        
    def test_parent_roles(self):
        self.folder.invokeFactory('opengever.task.task', 'task-1')
        self.folder.get('task-1').responsible = 'testuser'
        e = AddLocalRolesAction()
        e.parent_roles = set(['Contributor'])
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.get('task-1'))), IExecutable)
        self.assertEquals(True, ex())
        local_roles = dict(self.folder.get_local_roles())
        self.assertEquals(('Contributor',), local_roles.get('testuser'))

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
