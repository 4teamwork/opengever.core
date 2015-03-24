from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity.model import Activity
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER
from opengever.testing import FunctionalTestCase


class TestForwardingActivites(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER

    def setUp(self):
        super(TestForwardingActivites, self).setUp()
        self.inbox = create(Builder('inbox').titled(u'Inbox'))
        self.document = create(Builder('dossier').titled(u'Document'))

        self.hugo = create(Builder('ogds_user')
                           .id('hugo.boss')
                           .assign_to_org_units([self.org_unit])
                           .having(firstname=u'Hugo', lastname=u'Boss'))

        create(Builder('ogds_user')
               .id('peter.mueller')
               .assign_to_org_units([self.org_unit])
               .having(firstname=u'Peter', lastname=u'M\xfcller'))

    @browsing
    def test_forwarding_added(self, browser):
        browser.login().open(
            self.inbox, view='++add++opengever.inbox.forwarding',
            data={'paths': ['/'.join(self.document.getPhysicalPath())]})

        browser.fill({'Title': u'Abkl\xe4rung Fall Meier',
                      'Responsible': u'hugo.boss',
                      'Deadline': '02/13/15',
                      'Text': 'Lorem ipsum'})
        browser.find('Save').click()

        activity = Activity.query.first()
        self.assertEquals('forwarding-added', activity.kind)
        self.assertEquals(u'Abkl\xe4rung Fall Meier', activity.title)
        self.assertEquals(u'New forwarding added by Test User',
                          activity.summary)
