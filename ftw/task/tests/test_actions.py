from zope.component.interfaces import IObjectEvent
from zope.interface import implements
from zope.component import getUtility, getMultiAdapter
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IRuleAction
from plone.contentrules.rule.interfaces import IExecutable
from plone.app.contentrules.rule import Rule
from ftw.task.tests.base import TestCase
from ftw.task.actions.addlocalroles import AddLocalRolesAction, AddLocalRolesEditForm

class DummyEvent(object):
    implements(IObjectEvent)
    
    def __init__(self, object):
        self.object = object

class TestAddLocalRolesAction(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.folder.invokeFactory('Folder', 'f1')
        self.folder.f1.invokeFactory('Document', 'd1')
        #self.folder.invokeFactory('ftw.task.task', 't1')
        #self.folder.t1.setRelatedItems(self.folder.f1.d2)

    def testRegistered(self): 
        element = getUtility(IRuleAction, name='ftw.task.actions.AddLocalRoles')
        self.assertEquals('ftw.task.actions.AddLocalRoles', element.addview)
        self.assertEquals('edit', element.editview)
        self.assertEquals(None, element.for_)
        self.assertEquals(IObjectEvent, element.event)

    def testInvokeAddView(self): 
        element = getUtility(IRuleAction, name='ftw.task.actions.AddLocalRoles')
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')
        
        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+action')
        addview = getMultiAdapter((adding, self.portal.REQUEST), name=element.addview)
        
        addview.createAndAdd(data={'role_names': set(['Reader'])})
        
        e = rule.actions[0]
        self.failUnless(isinstance(e, AddLocalRolesAction))
        self.assertEquals(set(['Reader']), e.role_names)
    
    def testInvokeEditView(self): 
        element = getUtility(IRuleAction, name='ftw.task.actions.AddLocalRoles')
        e = AddLocalRolesAction()
        editview = getMultiAdapter((e, self.folder.REQUEST), name=element.editview)
        self.failUnless(isinstance(editview, AddLocalRolesEditForm))
    
    # def testExecute(self): 
    #     e = AddLocalRolesAction()
    #     e.role_names = set(['Reader'])
    #     e.check_types = None
    #     
    #     ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.f1.d1)), IExecutable)
    #     self.assertEquals(True, ex())
    #     
    #     self.assertEquals('published', self.portal.portal_workflow.getInfoFor(self.folder.f1, 'review_state'))
