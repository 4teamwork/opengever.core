from opengever.ogds.base import contact_info
from opengever.task.response import Base
from plone.dexterity.utils import createContent, addContentToContainer
from z3c.form import testing
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.component import getMultiAdapter
from zope.component import provideUtility
from zope.event import notify
from zope.globalrequest import setRequest
from zope.interface import alsoProvides, implements
from zope.lifecycleevent import ObjectCreatedEvent, ObjectAddedEvent
import unittest2 as unittest
from opengever.task.testing import OPENGEVER_TASK_INTEGRATION_TESTING
import transaction

class MockedContactInformation(contact_info.ContactInformation):
    implements(contact_info.IContactInformation)

    def _refresh_users(self, force=False):
        pass


class TestResponse(unittest.TestCase):

    layer = OPENGEVER_TASK_INTEGRATION_TESTING

    def setUp(self):
        # Set up z3c.form defaults
        testing.setupFormDefaults()
        # mock tentacle
        provideUtility(MockedContactInformation())
        # create task for testing
        createContent('opengever.task.task')
        task = createContent('opengever.task.task', title='Task')
        notify(ObjectCreatedEvent(task))
        task = addContentToContainer(self.layer['portal'], task, checkConstraints=False)
        notify(ObjectAddedEvent(task))
        transaction.commit()

    def test_base_view(self):
        context = self.layer['portal'].get('task-1')
        request = self.layer['request']

        request['ACTUAL_URL'] = context.absolute_url()
        view = Base(context, request)
        self.assertEquals([], view.responses())

    def test_add_form(self):
        request = self.layer['request']
        request.LANGUAGE = 'de'
        setRequest(request)
        alsoProvides(request, IAttributeAnnotatable)
        task1 = self.layer['portal'].get('task-1')
        request['ACTUAL_URL'] = task1.absolute_url()
        view = getMultiAdapter((task1, request),
                                name=u'addresponse').__of__(task1)
        view.update()
        self.failUnless('form.buttons.save' in view.render())

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
