from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase
from opengever.testing import OPENGEVER_FUNCTIONAL_TESTING
from plone.dexterity.utils import createContentInContainer
import transaction


class TestForwarding(FunctionalTestCase):
    layer = OPENGEVER_FUNCTIONAL_TESTING
    use_browser = True

    def setUp(self):
        super(TestForwarding, self).setUp()
        self.grant('Owner', 'Editor', 'Contributor')

        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture')
            .with_user()
            .with_org_unit(client_id='plone')
            .with_admin_unit())

    def test_forwarding(self):
        # create inbox and some documents for tests
        inbox = createContentInContainer(self.portal, 'opengever.inbox.inbox', title=u'inbox')
        doc1 = createContentInContainer(inbox, 'opengever.document.document',title=u'Document for a forwarding')
        doc2 = createContentInContainer(inbox, 'opengever.document.document',title=u'second Document for a forwarding')
        transaction.commit()

        # test forwarding creation
        # In Inboxes we should not be able to add forwardings using the factorymenu
        self.browser.open(inbox.absolute_url())
        self.assertPageContainsNot('/++add++opengever.inbox.forwarding')
        # Creating a Forwarding without any documetn should not be possible
        self.browser.open('%s/++add++opengever.inbox.forwarding' % inbox.absolute_url())
        self.assertPageContains('Error: Please select at least one document to forward')

        # create a forwarding with two documents
        data = 'paths:list=%s&paths:list=%s' % ('/'.join(doc1.getPhysicalPath()),'/'.join(doc2.getPhysicalPath()))
        self.browser.open('%s/++add++opengever.inbox.forwarding' % inbox.absolute_url(), data=data)

        self.browser.getControl(name='form.widgets.title').value = 'Dossier Test'

        # check defaults
        self.assertEquals(['inbox:plone'], self.browser.getControl(name='form.widgets.issuer:list').value)

        self.assertEquals(['inbox:plone'], self.browser.getControl(name='form.widgets.responsible:list').value)

        self.assertEquals(['plone'], self.browser.getControl(name='form.widgets.responsible_client:list').value)

        # create forwarding and check if documents are corectly moved
        self.browser.getControl(name="form.buttons.save").click()
        forwarding = inbox.get('forwarding-1')
        self.assertEqual(['forwarding-1'], inbox.objectIds())
        self.assertEquals(['document-1', 'document-2'], forwarding.objectIds())

        # check view
        self.browser.open(forwarding.absolute_url())
