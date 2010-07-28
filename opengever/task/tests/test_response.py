from zope.component import getMultiAdapter
from zope.interface import alsoProvides

from Products.PloneTestCase.ptc import PloneTestCase

from z3c.form import testing
from zope.annotation.interfaces import IAttributeAnnotatable

from opengever.task.tests.layer import Layer
from opengever.task.response import Base

class TestResponse(PloneTestCase):
    
    layer = Layer
    
    def afterSetUp(self):
        # Set up z3c.form defaults
        testing.setupFormDefaults()
        self.folder.invokeFactory('opengever.task.task', 'task')

    def test_base_view(self):
        view = Base(self.folder.task, testing.TestRequest())
        self.assertEquals([], view.responses())
        
    def test_add_form(self):
        request = testing.TestRequest()
        alsoProvides(request, IAttributeAnnotatable)
        view = getMultiAdapter((self.folder.task, request), name=u'addresponse').__of__(self.folder.task)
        view.update()
        self.failUnless('form.buttons.add' in view.render())


        