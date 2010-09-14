from zope.component import getMultiAdapter
from zope.component import provideUtility
from zope.interface import alsoProvides, implements

from Products.PloneTestCase.ptc import PloneTestCase

from z3c.form import testing
from zope.annotation.interfaces import IAttributeAnnotatable

from opengever.octopus.tentacle import contact_info

from opengever.task.tests.layer import Layer
from opengever.task.response import Base

class MockedContactInformation(contact_info.ContactInformation):
    implements(contact_info.IContactInformation)
    def _refresh_users(self, force=False):
        pass

class TestResponse(PloneTestCase):
    
    layer = Layer
    
    def afterSetUp(self):
        # Set up z3c.form defaults
        testing.setupFormDefaults()
        # mock tentacle
        provideUtility(MockedContactInformation())
        # create task for testing
        self.folder.invokeFactory('opengever.task.task', 'task-1')

    def test_base_view(self):
        view = Base(self.folder.get('task-1'), self.app.REQUEST)
        self.assertEquals([], view.responses())

    def test_add_form(self):
        request = self.app.REQUEST
        request.LANGUAGE = 'de'
        alsoProvides(request, IAttributeAnnotatable)
        task1 = self.folder.get('task-1')
        view = getMultiAdapter((task1, request),
                                name=u'addresponse').__of__(task1)
        view.update()
        self.failUnless('form.buttons.add' in view.render())
