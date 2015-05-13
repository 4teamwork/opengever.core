from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity import notification_center
from opengever.activity.model import Activity
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER
from opengever.task.browser.accept.utils import assign_forwarding_to_dossier
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


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

    @browsing
    def test_assign_forwarding_to_dossier_add_responsible_and_issuer_to_successors_watcherlist(self, browser):
        dossier = create(Builder('dossier').titled(u'Dossier A'))
        inbox = create(Builder('inbox').titled(u'Inbox'))
        forwarding = create(Builder('forwarding')
                            .within(inbox)
                            .having(issuer='inbox:client2',
                                    responsible='hugo.boss')
                            .titled(u'Anfrage XY'))

        task = assign_forwarding_to_dossier(self.portal, forwarding.oguid.id,
                                            dossier, "Ok!")

        # The responsible of the task is the `inbox:client1`,
        # but the PloneNotificationCenter adds every actor representative.
        self.assertEquals(
            [TEST_USER_ID, 'hugo.boss'],
            [watcher.user_id for watcher in notification_center().get_watchers(task)])
