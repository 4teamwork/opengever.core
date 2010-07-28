import unittest

from zope.component import createObject
from zope.component import queryUtility, getUtility

from plone.dexterity.interfaces import IDexterityFTI

from Products.PloneTestCase.ptc import PloneTestCase
from plone.registry.interfaces import IRegistry


from opengever.task.tests.layer import Layer
from opengever.task.task import ITask
from opengever.task.adapters import IResponseContainer
from opengever.task.response import Response

class TestTaskIntegration(PloneTestCase):
    
    layer = Layer
    
    def test_adding(self):
        self.folder.invokeFactory('opengever.task.task', 'task1')
        t1 = self.folder['task1']
        self.failUnless(ITask.providedBy(t1))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='opengever.task.task')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='opengever.task.task')
        schema = fti.lookupSchema()
        self.assertEquals(ITask, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='opengever.task.task')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(ITask.providedBy(new_object))

    def test_view(self):
        self.folder.invokeFactory('opengever.task.task', 'task1')
        t1 = self.folder['task1']
        view = t1.restrictedTraverse('@@view')
        self.failUnless(len(view.getSubTasks())==0)
        t1.invokeFactory('opengever.task.task','task2')
        t2 = t1['task2']
        self.failUnless(view.getSubTasks()[0].getObject()==t2)

    def test_addresponse(self):
        self.folder.invokeFactory('opengever.task.task', 'task1')
        t1 = self.folder['task1']
        res = Response("")
        container = IResponseContainer(t1)
        container.add(res)
        self.failUnless(res in container)

    def test_task_type_category(self):
        self.folder.invokeFactory('opengever.task.task', 'task1')
        t1 = self.folder['task1']
        registry = getUtility(IRegistry)
        registry['opengever.task.interfaces.ITaskSettings.task_types_uni_ref'] = [u'Uni Ref 1',]
        t1.task_type = u'Uni Ref 1'
        self.assertEquals(u'uni_ref', t1.task_type_category)
        registry['opengever.task.interfaces.ITaskSettings.task_types_uni_val'] = [u'Uni Val 1', u'Uni Val 2']
        t1.task_type = u'Uni Val 2'
        self.assertEquals(u'uni_val', t1.task_type_category)        
        
def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)