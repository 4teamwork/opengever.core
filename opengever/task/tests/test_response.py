from Products.PloneTestCase.ptc import PloneTestCase
from opengever.ogds.base import contact_info
from opengever.task.adapters import Response
from opengever.task.response import Base
from opengever.task.tests.layer import Layer
from plone.dexterity.utils import createContent, addContentToContainer
from z3c.form import testing
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.component import getMultiAdapter
from zope.component import provideUtility
from zope.event import notify
from zope.globalrequest import setRequest
from zope.interface import alsoProvides, implements
from zope.lifecycleevent import ObjectCreatedEvent, ObjectAddedEvent
import datetime


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
        createContent('opengever.task.task')
        task = createContent('opengever.task.task', title='Task')
        notify(ObjectCreatedEvent(task))
        task = addContentToContainer(self.folder, task, checkConstraints=False)
        notify(ObjectAddedEvent(task))

    def test_base_view(self):
        view = Base(self.folder.get('task-1'), self.app.REQUEST)
        self.assertEquals([], view.responses())

    def test_add_form(self):
        request = self.app.REQUEST
        request.LANGUAGE = 'de'
        setRequest(request)
        alsoProvides(request, IAttributeAnnotatable)
        task1 = self.folder.get('task-1')
        view = getMultiAdapter((task1, request),
                                name=u'addresponse').__of__(task1)
        view.update()
        self.failUnless('form.buttons.add' in view.render())

    def test_asdf(self):
        task = self.folder.get('task-1')

        new_response = Response('')
        self.assertNotEqual(new_response, None)

        form = {
            'transition:list': 'task-transition-open-resolved',
            'form.widgets.transition-empty-marker': '1',
            'form.widgets.relatedItems-empty-marker': '1',
            'LANGUAGE': 'de',
            'form.buttons.add': 'Hinzufuegen',
            'form.widgets.new_responsible:list': '--NOVALUE--',
            'form.widgets.new_responsible-empty-marker': '1',
        }
        self.app.REQUEST.form = form
        self.app.REQUEST.form.update()
        addform = task.unrestrictedTraverse('addresponse')
        setattr(addform.form, 'extractData', lambda a: [{
            'transition':'task-transition-open-resolved',
            'relatedItems': [],
            }, None])
        addform()
        self.failUnless(
            task.date_of_completion == datetime.datetime.now().date())
