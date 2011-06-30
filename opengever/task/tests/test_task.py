from datetime import datetime
from Products.PloneTestCase.ptc import PloneTestCase
from opengever.task.adapters import IResponseContainer
from opengever.task.response import Response
from opengever.task.task import ITask
from opengever.task.tests.layer import Layer
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContent, addContentToContainer
from zope.component import createObject
from zope.component import queryUtility
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent, ObjectAddedEvent
import unittest


def create_task(parent, **kwargs):
    createContent('opengever.task.task')
    task = createContent('opengever.task.task', **kwargs)
    notify(ObjectCreatedEvent(task))
    task = addContentToContainer(parent, task, checkConstraints=False)
    notify(ObjectAddedEvent(task))
    return task


class TestTaskIntegration(PloneTestCase):

    layer = Layer

    def afterSetUp(self):
        self.portal.portal_types['opengever.task.task'].global_allow = True

    def test_adding(self):
        t1 = create_task(self.folder, title='Task 1')
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
        t1 = create_task(self.folder, title='Task 1')
        view = t1.restrictedTraverse('@@tabbedview_view-overview')
        self.failUnless(len(view.getSubTasks())==0)
        t2 = create_task(t1, title='Task 2')
        self.failUnless(view.getSubTasks()[0].getObject()==t2)

    def test_addresponse(self):
        t1 = create_task(self.folder, title='Task 1')
        res = Response("")
        container = IResponseContainer(t1)
        container.add(res)
        self.failUnless(res in container)

    def test_task_type_category(self):
        t1 = create_task(self.folder, title='Task 1')
        t1.task_type = u'information'
        self.assertEquals(u'unidirectional_by_reference', t1.task_type_category)
        t1.task_type = u'approval'
        self.assertEquals(u'bidirectional_by_reference', t1.task_type_category)

    def test_task_date_subscriber(self):
        t1 = create_task(self.folder, title='Task 1')
        wft = t1.portal_workflow
        
        self.failUnless(t1.expectedStartOfWork == None)
        wft.doActionFor(t1, 'task-transition-open-in-progress')
        self.failUnless(t1.expectedStartOfWork.date() == datetime.now().date())

        self.failUnless(t1.date_of_completion == None)
        wft.doActionFor(t1, 'task-transition-in-progress-resolved')
        self.failUnless(t1.date_of_completion.date() == datetime.now().date())

        wft.doActionFor(t1, 'task-transition-resolved-open')
        self.failUnless(t1.date_of_completion == None)

        t2 = create_task(self.folder, title='Task 2')
        self.failUnless(t2.date_of_completion == None)
        wft.doActionFor(t2, 'task-transition-open-tested-and-closed')
        self.failUnless(t2.date_of_completion.date() == datetime.now().date())

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
