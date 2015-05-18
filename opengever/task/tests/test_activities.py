from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testing.mailing import Mailing
from opengever.activity import notification_center
from opengever.activity.model import Activity
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER
from opengever.task.browser.accept.utils import accept_task_with_successor
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestTaskActivites(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER

    def setUp(self):
        super(TestTaskActivites, self).setUp()
        self.dossier = create(Builder('dossier').titled(u'Dossier XY'))

        self.hugo = create(Builder('ogds_user')
                           .id('hugo.boss')
                           .assign_to_org_units([self.org_unit])
                           .having(firstname=u'Hugo', lastname=u'Boss'))

    @browsing
    def test_task_added(self, browser):
        browser.login().open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title': u'Abkl\xe4rung Fall Meier',
                      'Responsible': u'hugo.boss',
                      'Task Type': 'comment',
                      'Deadline': '02/13/15',
                      'Text': 'Lorem ipsum'})
        browser.css('#form-buttons-save').first.click()

        activity = Activity.query.first()
        self.assertEquals('task-added', activity.kind)
        self.assertEquals(u'Abkl\xe4rung Fall Meier', activity.title)
        self.assertEquals(u'New task added by Test User', activity.summary)

        # XXX should be a better assertion like the ftw.testbrowser table
        # dict representation
        self.maxDiff = None
        expected = (u'<table><tbody>'
                    u'<tr><th>Task title</th><td>Abkl\xe4rung Fall Meier</td></tr>'
                    u'<tr><th>Deadline</th><td>Feb 13, 2015</td></tr>'
                    u'<tr><th>Task Type</th><td>To comment</td></tr>'
                    u'<tr><th>Dossier title</th><td>Dossier XY</td></tr>'
                    u'<tr><th>Text</th><td>Lorem ipsum</td></tr></tbody></table>')
        self.assertEquals(expected, activity.description)

    @browsing
    def test_adding_task_adds_responsible_and_issuer_to_watchers(self, browser):
        browser.login().open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title': u'Abkl\xe4rung Fall Meier',
                      'Responsible': u'hugo.boss',
                      'Task Type': 'comment',
                      'Text': 'Lorem ipsum'})
        browser.css('#form-buttons-save').first.click()

        center = notification_center()
        watchers = center.get_watchers(self.dossier.listFolderContents()[0])
        self.assertItemsEqual(
            ['hugo.boss', TEST_USER_ID],
            [watcher.user_id for watcher in watchers])

    @browsing
    def test_task_accepted(self, browser):
        task = create(Builder('task')
                      .titled(u'Abkl\xe4rung Fall Meier')
                      .having(responsible=TEST_USER_ID))

        browser.login().open(task)
        browser.css('#workflow-transition-task-transition-open-in-progress').first.click()
        browser.fill({'Response': u'Wird n\xe4chste Woche erledigt.'})
        browser.css('#form-buttons-save').first.click()

        activity = Activity.query.first()
        self.assertEquals(u'task-transition-open-in-progress', activity.kind)
        self.assertEquals(u'Abkl\xe4rung Fall Meier', activity.title)
        self.assertEquals(
            u'Accepted by <a href="http://nohost/plone/@@user-details/test_user_1_">Test User (test_user_1_)</a>',
            activity.summary)
        self.assertEquals(u'Wird n\xe4chste Woche erledigt.', activity.description)

    @browsing
    def test_activity_actor_is_current_user(self, browser):
        create(Builder('user')
               .with_userid('hugo.boss')
               .with_roles('Reader', 'Editor', 'Contributor'))
        task = create(Builder('task')
                      .titled(u'Abkl\xe4rung Fall Meier')
                      .having(responsible='hugo.boss'))

        browser.login(username='hugo.boss', password='secret').open(task)
        browser.css('#workflow-transition-task-transition-open-in-progress').first.click()
        browser.fill({'Response': u'Wird n\xe4chste Woche erledigt.'})
        browser.css('#form-buttons-save').first.click()

        activity = Activity.query.first()
        self.assertEquals(u'task-transition-open-in-progress', activity.kind)
        self.assertEquals('hugo.boss', activity.actor_id)

    @browsing
    def test_task_resolved(self, browser):
        task = create(Builder('task')
                      .titled(u'Abkl\xe4rung Fall Meier')
                      .having(responsible=TEST_USER_ID)
                      .in_state('task-state-in-progress'))

        browser.login().open(task)
        browser.css('#workflow-transition-task-transition-in-progress-resolved').first.click()
        browser.fill({'Response': u'Ist erledigt.'})
        browser.css('#form-buttons-save').first.click()

        activity = Activity.query.first()
        self.assertEquals(u'task-transition-in-progress-resolved', activity.kind)
        self.assertEquals(u'Abkl\xe4rung Fall Meier', activity.title)
        self.assertEquals(
            u'Resolved by <a href="http://nohost/plone/@@user-details/test_user_1_">Test User (test_user_1_)</a>', activity.summary)
        self.assertEquals(u'Ist erledigt.', activity.description)

    @browsing
    def test_deadline_modified_activity(self, browser):
        task = create(Builder('task')
                      .titled(u'Abkl\xe4rung Fall Meier')
                      .having(responsible=u'hugo.boss',
                              deadline=date(2015, 03, 01))
                      .in_state('task-state-in-progress'))

        browser.login().open(
            task, view='modify_deadline',
            data={'form.widgets.transition': 'task-transition-modify-deadline'})

        browser.fill({
            'New Deadline': '03/20/16',
            'Response': u'nicht dring\xe4nd'}).save()

        activity = Activity.query.first()
        self.assertEquals(u'task-transition-modify-deadline', activity.kind)
        self.assertEquals(u'Abkl\xe4rung Fall Meier', activity.title)
        self.assertEquals(
            'Deadline modified from 01.03.2015 to 20.03.2016 by'
            ' <a href="http://nohost/plone/@@user-details/test_user_1_">'
            'Test User (test_user_1_)</a>', activity.summary)
        self.assertEquals(u'nicht dring\xe4nd', activity.description)

    @browsing
    def test_adding_a_subtask_notifies_watchers(self, browser):
        task = create(Builder('task')
                      .titled(u'Abkl\xe4rung Fall Meier')
                      .having(responsible=u'hugo.boss',
                              deadline=date(2015, 03, 01))
                      .in_state('task-state-in-progress'))

        browser.login().open(task, view='++add++opengever.task.task')
        browser.fill({'Title': u'Abkl\xe4rung Fall Meier',
                      'Responsible': 'hugo.boss',
                      'Issuer': u'hugo.boss',
                      'Task Type': 'comment',
                      'Text': 'Lorem ipsum'})
        browser.css('#form-buttons-save').first.click()

        activity = Activity.query.first()
        self.assertEquals(u'transition-add-subtask', activity.kind)

    @browsing
    def test_adding_a_document_notifies_watchers(self, browser):
        task = create(Builder('task')
                      .titled(u'Abkl\xe4rung Fall Meier')
                      .having(responsible=u'hugo.boss',
                              deadline=date(2015, 03, 01))
                      .in_state('task-state-in-progress'))

        browser.login().open(task, view='++add++opengever.document.document')
        browser.fill({'Title': u'Letter to peter'})
        browser.css('#form-buttons-save').first.click()

        activity = Activity.query.first()
        self.assertEquals(u'transition-add-document', activity.kind)


class TestTaskReassignActivity(TestTaskActivites):

    def setUp(self):
        super(TestTaskReassignActivity, self).setUp()

        create(Builder('ogds_user')
               .id('peter.meier')
               .assign_to_org_units([self.org_unit])
               .having(firstname=u'Peter', lastname=u'Meier'))
        create(Builder('ogds_user')
               .id('james.meier')
               .assign_to_org_units([self.org_unit])
               .having(firstname=u'James', lastname=u'Meier'))

    def add_task(self, browser):
        browser.login().open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title': u'Abkl\xe4rung Fall Meier',
                      'Responsible': 'james.meier',
                      'Issuer': u'peter.meier',
                      'Task Type': 'comment',
                      'Text': 'Lorem ipsum'})
        browser.css('#form-buttons-save').first.click()
        return self.dossier.get('task-1')

    def reassign(self, browser, responsible, response):
        browser.login().open(self.task)
        browser.css('#workflow-transition-task-transition-reassign').first.click()
        browser.fill({'Responsible': responsible,
                      'Response': response})
        browser.css('#form-buttons-save').first.click()

    @browsing
    def test_properties(self, browser):
        self.task = self.add_task(browser)
        self.reassign(browser, 'hugo.boss', u'Bitte Abkl\xe4rungen erledigen.')

        activity = Activity.query.all()[-1]

        self.assertEquals(u'task-transition-reassign', activity.kind)
        self.assertEquals(u'Abkl\xe4rung Fall Meier', activity.title)
        self.assertEquals(u'Reassigned from <a href="http://nohost/plone/@@user-details/james.meier">Meier James (james.meier)</a> to <a href="http://nohost/plone/@@user-details/hugo.boss">Boss Hugo (hugo.boss)</a> by <a href="http://nohost/plone/@@user-details/test_user_1_">Test User (test_user_1_)</a>', activity.summary)
        self.assertEquals(u'Bitte Abkl\xe4rungen erledigen.', activity.description)

    @browsing
    def test_notifies_old_and_new_responsible(self, browser):
        self.task = self.add_task(browser)
        self.reassign(browser, 'hugo.boss', u'Bitte Abkl\xe4rungen erledigen.')

        activity = Activity.query.all()[-1]

        self.assertItemsEqual(
            [u'james.meier', u'peter.meier', u'hugo.boss'],
            [notes.watcher.user_id for notes in activity.notifications])

    @browsing
    def test_removes_old_responsible_from_watchers_list(self, browser):
        self.task = self.add_task(browser)
        self.reassign(browser, 'hugo.boss', u'Bitte Abkl\xe4rungen erledigen.')

        watchers = notification_center().get_watchers(self.task)
        self.assertItemsEqual(
            ['peter.meier', 'hugo.boss'],
            [watcher.user_id for watcher in watchers])


class TestSuccesssorHandling(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER

    def setUp(self):
        super(TestSuccesssorHandling, self).setUp()

        # we need to setup the mock mailhost to avoid problems when using
        # transaction savepoints
        Mailing(self.portal).set_up()

        create(Builder('ogds_user')
               .id('peter.meier')
               .assign_to_org_units([self.org_unit]))
        create(Builder('ogds_user')
               .id('james.meier')
               .assign_to_org_units([self.org_unit]))
        create(Builder('ogds_user')
               .id('hugo.boss')
               .assign_to_org_units([self.org_unit]))

        self.center = notification_center()
        self.dossier = create(Builder('dossier').titled(u'Dosssier A'))
        self.predecessor = create(Builder('task')
                                  .having(responsible='peter.meier',
                                          issuer='james.meier'))

        self.center.add_watcher_to_resource(self.predecessor, 'peter.meier')
        self.center.add_watcher_to_resource(self.predecessor, 'hugo.boss')
        self.center.add_watcher_to_resource(self.predecessor, 'james.meier')

    def tearDown(self):
        super(TestSuccesssorHandling, self).tearDown()
        Mailing(self.layer['portal']).tear_down()

    def test_when_accepting_task_with_successor_responsible_watcher_gets_moved_from_predecessor_to_successsor(self):
        successor = accept_task_with_successor(
            self.dossier, self.predecessor.oguid.id, 'Ok.')

        predecessors_watcher = [watcher.user_id for watcher in
                                self.center.get_watchers(self.predecessor)]
        successors_watcher = [watcher.user_id for watcher in
                              self.center.get_watchers(successor)]
        self.assertItemsEqual(['hugo.boss', 'james.meier'], predecessors_watcher)
        self.assertEquals(['peter.meier'], successors_watcher)
