import unittest2 as unittest

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from opengever.inbox.testing import OPENGEVER_INBOX_INTEGRATION_TESTING

from opengever.inbox.inbox import IInbox

class TestInboxIntegration(unittest.TestCase):

    layer = OPENGEVER_INBOX_INTEGRATION_TESTING

    def test_adding(self):
        portal = self.layer['portal']
        portal.invokeFactory('opengever.inbox.inbox', 'inbox1')
        i1 = portal['inbox1']
        self.failUnless(IInbox.providedBy(i1))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='opengever.inbox.inbox')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='opengever.inbox.inbox')
        schema = fti.lookupSchema()
        self.assertEquals(IInbox, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='opengever.inbox.inbox')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IInbox.providedBy(new_object))

    def test_view(self):
        portal = self.layer['portal']
        request = self.layer['request']
        request.set('URL', portal.absolute_url() + '/@@folder_contents')
        request.set('ACTUAL_URL', portal.absolute_url() + '/@@folder_contents')
        portal.invokeFactory('opengever.inbox.inbox', 'inbox1')
        i1 = portal['inbox1']
        view = i1.restrictedTraverse('@@view')
        self.failUnless(view())

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
