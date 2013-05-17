from datetime import datetime
from opengever.task.adapters import IResponseContainer
from opengever.task.response import Response
from opengever.task.task import ITask
from opengever.testing import Builder
from opengever.testing import FunctionalTestCase
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContent, addContentToContainer
from z3c.relationfield.relation import RelationValue
from zope.component import createObject
from zope.component import getUtility
from zope.component import queryUtility
from zope.event import notify
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectCreatedEvent, ObjectAddedEvent
import unittest2 as unittest


def create_task(parent, **kwargs):
    createContent('opengever.task.task')
    task = createContent('opengever.task.task', **kwargs)
    notify(ObjectCreatedEvent(task))
    task = addContentToContainer(parent, task, checkConstraints=False)
    notify(ObjectAddedEvent(task))
    return task


class TestTaskIntegration(FunctionalTestCase):

    def setUp(self):
        super(TestTaskIntegration, self).setUp()
        self.portal.portal_types['opengever.task.task'].global_allow = True

    def test_adding(self):
        t1 = create_task(self.portal, title='Task 1')
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
        t1 = create_task(self.portal, title='Task 1')
        view = t1.restrictedTraverse('@@tabbedview_view-overview')
        self.failUnless(len(view.get_sub_tasks()) == 0)
        t2 = create_task(t1, title='Task 2')
        self.failUnless(view.get_sub_tasks()[0] == t2)

    def test_relateddocuments(self):
        self.grant('Manager')
        # create document and append it to the relatedItems of the task
        doc3 = Builder("document").titled("a-testthree").create()
        intids = getUtility(IIntIds)
        o_iid = intids.getId(doc3)
        t1 = create_task(
            self.portal, title='Task 1', relatedItems=[RelationValue(o_iid)])
        doc1 = Builder("document").within(t1).titled("btestone").create()
        doc2 = Builder("document").within(t1).titled("ctesttwo").create()
        view = t1.restrictedTraverse('tabbedview_view-relateddocuments')
        results = [aa.Title for aa in view.table_source.build_query()]
        self.assertTrue(doc3.Title() in results)

        #check sorting
        view.request.set('sort', u'sortable_title')
        results = [aa.Title for aa in view.table_source.build_query()]
        self.assertTrue(results == [doc3.Title(), doc1.Title(), doc2.Title()])

        view.request.set('ACTUAL_URL', t1.absolute_url())
        self.failUnless(view())

    def test_addresponse(self):
        t1 = create_task(self.portal, title='Task 1')
        res = Response("")
        container = IResponseContainer(t1)
        container.add(res)
        self.failUnless(res in container)

    def test_task_type_category(self):
        t1 = create_task(self.portal, title='Task 1')
        t1.task_type = u'information'
        self.assertEquals(
            u'unidirectional_by_reference', t1.task_type_category)
        t1.task_type = u'approval'
        self.assertEquals(
            u'bidirectional_by_reference', t1.task_type_category)

    def test_task_date_subscriber(self):
        t1 = create_task(self.portal, title='Task 1')
        member = self.portal.restrictedTraverse('plone_portal_state').member()
        t1.responsible = str(member)
        t1.issuer = str(member)
        wft = t1.portal_workflow

        self.failUnless(t1.expectedStartOfWork == None)
        wft.doActionFor(t1, 'task-transition-open-in-progress')
        self.failUnless(t1.expectedStartOfWork.date() == datetime.now().date())

        self.failUnless(t1.date_of_completion == None)
        wft.doActionFor(t1, 'task-transition-in-progress-resolved')
        self.failUnless(t1.date_of_completion.date() == datetime.now().date())

        wft.doActionFor(t1, 'task-transition-resolved-in-progress')
        self.failUnless(t1.date_of_completion == None)

        t2 = create_task(self.portal, title='Task 2')
        t2.issuer = str(member)
        self.failUnless(t2.date_of_completion == None)
        wft.doActionFor(t2, 'task-transition-open-tested-and-closed')
        self.failUnless(t2.date_of_completion.date() == datetime.now().date())

    def test_subtask_response(self):
        """When a subtask is added it should automaticly
        add a response on maintask"""

        intids = getUtility(IIntIds)
        maintask = create_task(self.portal, title='maintask')
        subtask = create_task(maintask, title='subtask')
        responses = IResponseContainer(maintask)
        self.assertEquals(
            responses[-1].added_object.to_id, intids.getId(subtask))
        self.assertEquals(len(responses), 2)

        # all different remote requests should not
        # generate an response
        maintask.REQUEST.environ['X_OGDS_AC'] = 'hugo.boss'
        create_task(maintask, title='subtask')
        self.assertEquals(len(IResponseContainer(maintask)), 2)

        maintask.REQUEST.environ['X_OGDS_AC'] = None
        maintask.REQUEST.environ['X_OGDS_CID'] = 'client_a'
        create_task(maintask, title='subtask')
        self.assertEquals(len(IResponseContainer(maintask)), 2)

        maintask.REQUEST.environ['X_OGDS_CID'] = None
        maintask.REQUEST.set('X-CREATING-SUCCESSOR', True)
        create_task(maintask, title='subtask')
        self.assertEquals(len(IResponseContainer(maintask)), 2)
