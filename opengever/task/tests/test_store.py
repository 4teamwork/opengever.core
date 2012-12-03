from Products.CMFCore.utils import getToolByName
from datetime import datetime
from ftw.testing import MockTestCase
from opengever.task.adapters import IResponseContainer
from opengever.task.testing import OPENGEVER_TASK_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from plone.dexterity.utils import createContentInContainer
from plone.testing.z2 import Browser
import transaction


class TestForwardingStore(MockTestCase):

    layer = OPENGEVER_TASK_INTEGRATION_TESTING

    def setUp(self):
        super(TestForwardingStore, self).setUp()
        self.app = self.layer.get('app')
        self.portal = self.layer.get('portal')

        self.inbox = createContentInContainer(
            self.portal, 'opengever.inbox.inbox', title='inbox')

        self.forwarding = createContentInContainer(
            self.inbox, 'opengever.inbox.forwarding',
            title='forwarding1')

        self.browser = Browser(self.app)
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (
                TEST_USER_NAME, TEST_USER_PASSWORD,))
        transaction.commit()

    def test_forwarding_store_directly(self):

        self.browser.open(
            '%s/forwarding_close' % (self.forwarding.absolute_url()))
        self.browser.getControl(name='form.widgets.text').value = 'Lorem ipsum'
        self.browser.getControl(name='form.buttons.button_close').click()

        # check yearfolder
        yearfolder = self.inbox.get(str(datetime.now().year))
        self.assertTrue(yearfolder)

        # check forwarding
        forwarding = yearfolder.get('forwarding-1')
        self.assertTrue(forwarding)

        self.assertEquals(
            IResponseContainer(forwarding)[0].text, 'Lorem ipsum')

        wft = getToolByName(forwarding, 'portal_workflow')
        self.assertEquals(
            wft.getInfoFor(forwarding, 'review_state'),
            'forwarding-state-closed')
