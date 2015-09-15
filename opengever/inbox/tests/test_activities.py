from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity import notification_center
from opengever.activity.model import Activity
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER
from opengever.task.browser.accept.utils import accept_forwarding_with_successor
from opengever.task.browser.accept.utils import assign_forwarding_to_dossier
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestForwardingActivites(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER

    def setUp(self):
        super(TestForwardingActivites, self).setUp()
        self.center = notification_center()
        self.inbox = create(Builder('inbox').titled(u'Inbox'))
        self.document = create(Builder('document').titled(u'Document'))

        self.hugo = create(Builder('ogds_user')
                           .id('hugo.boss')
                           .assign_to_org_units([self.org_unit])
                           .having(firstname=u'Hugo', lastname=u'Boss'))

        create(Builder('ogds_user')
               .id('peter.mueller')
               .assign_to_org_units([self.org_unit])
               .in_group(self.org_unit.inbox_group)
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
        self.assertItemsEqual(
            [TEST_USER_ID, 'hugo.boss', 'peter.mueller'],
            [watcher.user_id for watcher in self.center.get_watchers(task)])

    @browsing
    def test_accepting_forwarding_with_successor_updated_responsibles(self, browser):
        inbox = create(Builder('inbox'))
        forwarding = create(Builder('forwarding')
                            .having(responsible=TEST_USER_ID,
                                    issuer='hugo.boss')
                            .within(inbox))
        self.center.add_watcher_to_resource(forwarding, TEST_USER_ID)
        self.center.add_watcher_to_resource(forwarding, 'hugo.boss')

        successor = accept_forwarding_with_successor(
            self.portal, forwarding.oguid.id,
            'OK. That is something for me.', dossier=None)

        self.assertItemsEqual(
            ['hugo.boss'],
            [watcher.user_id for watcher in self.center.get_watchers(forwarding)])
        self.assertItemsEqual(
            [TEST_USER_ID, 'peter.mueller'],
            [watcher.user_id for watcher in self.center.get_watchers(successor)])

    @browsing
    def test_accepting_and_assign_forwarding_with_successor_and__updated_responsibles(self, browser):
        inbox = create(Builder('inbox'))
        dossier = create(Builder('dossier'))
        forwarding = create(Builder('forwarding')
                            .having(responsible=TEST_USER_ID,
                                    issuer='hugo.boss')
                            .within(inbox))
        self.center.add_watcher_to_resource(forwarding, TEST_USER_ID)
        self.center.add_watcher_to_resource(forwarding, 'hugo.boss')

        task = accept_forwarding_with_successor(
            self.portal, forwarding.oguid.id,
            'OK. That is something for me.', dossier=dossier)

        self.assertItemsEqual(
            ['hugo.boss'],
            [watcher.user_id for watcher in self.center.get_watchers(forwarding)])
        self.assertItemsEqual(
            [TEST_USER_ID],
            [watcher.user_id for watcher in self.center.get_watchers(task)])


class TestForwardingReassignActivity(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER

    def setUp(self):
        super(TestForwardingReassignActivity, self).setUp()
        self.center = notification_center()
        self.inbox = create(Builder('inbox').titled(u'Inbox'))
        self.document = create(Builder('document')
                               .within(self.inbox)
                               .titled(u'Document'))

        self.hugo = create(Builder('ogds_user')
                           .id('hugo.boss')
                           .assign_to_org_units([self.org_unit])
                           .having(firstname=u'Hugo', lastname=u'Boss'))
        self.jon = create(Builder('ogds_user')
                          .id('jon.meier')
                          .assign_to_org_units([self.org_unit])
                          .having(firstname=u'Jon', lastname=u'Meier'))
        self.peter = create(Builder('ogds_user')
                            .id('peter.mueller')
                            .assign_to_org_units([self.org_unit])
                            .in_group(self.org_unit.inbox_group)
                            .having(firstname=u'Peter', lastname=u'M\xfcller'))

    def add_forwarding(self, browser):
        data = {'paths:list': ['/'.join(self.document.getPhysicalPath())]}
        browser.login().open(self.inbox, data,
                             view='++add++opengever.inbox.forwarding')
        browser.fill({'Title': u'Abkl\xe4rung Fall Meier',
                      'Responsible': 'jon.meier',
                      'Issuer': u'hugo.boss'})
        browser.css('#form-buttons-save').first.click()
        return self.inbox.get('forwarding-1')

    def reassign(self, browser, forwarding, responsible):
        browser.login().open(forwarding)
        browser.find('forwarding-transition-reassign').click()
        browser.fill({'Responsible': responsible,
                      'Response': u'Peter k\xf6nntest du das \xfcbernehmen.'})
        browser.find('Assign').click()

    @browsing
    def test_reassing_forwarding_create_notifications_for_all_participants(self, browser):
        forwarding = self.add_forwarding(browser)
        self.reassign(browser, forwarding, responsible='peter.mueller')

        self.assertEquals(2, len(Activity.query.all()))
        self.assertEquals(u'forwarding-added',
                          Activity.query.all()[0].kind)
        self.assertEquals(u'forwarding-transition-reassign',
                          Activity.query.all()[1].kind)

    @browsing
    def test_notifies_old_and_new_responsible(self, browser):
        forwarding = self.add_forwarding(browser)
        self.reassign(browser, forwarding, responsible='peter.mueller')

        activities = Activity.query.all()
        reassign_activity = activities[-1]
        self.assertItemsEqual(
            [u'jon.meier', u'peter.mueller', u'hugo.boss'],
            [notes.watcher.user_id for notes in reassign_activity.notifications])

    @browsing
    def test_removes_old_responsible_from_watchers_list(self, browser):
        forwarding = self.add_forwarding(browser)
        self.reassign(browser, forwarding, responsible='peter.mueller')

        watchers = notification_center().get_watchers(forwarding)
        self.assertItemsEqual(
            ['peter.mueller', u'hugo.boss'],
            [watcher.user_id for watcher in watchers])
