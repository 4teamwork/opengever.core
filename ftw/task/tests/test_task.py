import unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from Products.PloneTestCase.ptc import PloneTestCase
from ftw.task.tests.layer import Layer

from ftw.task.task import ITask

class TestTaskIntegration(PloneTestCase):
    
    layer = Layer
    
    def test_adding(self):
        self.folder.invokeFactory('ftw.task.task', 'task1')
        t1 = self.folder['task1']
        self.failUnless(ITask.providedBy(t1))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='ftw.task.task')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='ftw.task.task')
        schema = fti.lookupSchema()
        self.assertEquals(ITask, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='ftw.task.task')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(ITask.providedBy(new_object))

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)