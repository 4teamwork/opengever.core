from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.utils import get_header
from ftw.testbrowser import browsing
from ftw.testing.mailing import Mailing
from opengever.activity import notification_center
from opengever.activity.mailer import process_mail_queue
from opengever.activity.model import Activity
from opengever.activity.roles import TASK_ISSUER_ROLE
from opengever.activity.roles import TASK_RESPONSIBLE_ROLE
from opengever.activity.roles import WATCHER_ROLE
from opengever.base.model import create_session
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER
from opengever.ogds.base.actor import SYSTEM_ACTOR_ID
from opengever.ogds.models.user import User
from opengever.task.activities import TaskReminderActivity
from opengever.task.browser.accept.utils import accept_task_with_successor
from opengever.tasktemplates.interfaces import IFromSequentialTasktemplate
from opengever.testing import FunctionalTestCase
from opengever.testing import IntegrationTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
from sqlalchemy import desc
from zope.interface import alsoProvides
import email
import transaction


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
                      'Deadline': '13.02.2015',
                      'Text': 'Lorem ipsum'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('hugo.boss')

        browser.css('#form-buttons-save').first.click()

        activity = Activity.query.one()
        self.assertEquals('task-added', activity.kind)
        self.assertEquals(u'Abkl\xe4rung Fall Meier', activity.title)
        self.assertEquals(u'New task opened by Test User', activity.summary)

        browser.open_html(activity.description)
        rows = browser.css('table').first.rows

        self.assertEquals(
            [['Task title', u'Abkl\xe4rung Fall Meier'],
             ['Deadline', 'Feb 13, 2015'],
             ['Task Type', 'To comment'],
             ['Dossier title', 'Dossier XY'],
             ['Text', 'Lorem ipsum'],
             ['Responsible', 'Boss Hugo (hugo.boss)'],
             ['Issuer', 'Test User (test_user_1_)']],
            [row.css('td').text for row in rows])

    @browsing
    def test_private_task_added(self, browser):
        api.portal.set_registry_record(
            'opengever.task.interfaces.ITaskSettings.private_task_feature_enabled',
            True)
        browser.login().open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title': u'Abkl\xe4rung Fall Meier',
                      'Task Type': 'comment',
                      'Private task': True,
                      'Text': 'Lorem ipsum'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('hugo.boss')

        browser.css('#form-buttons-save').first.click()

        activity = Activity.query.one()
        self.assertEquals(u'New task (private) opened by Test User', activity.summary)

    @browsing
    def test_adding_task_adds_responsible_and_issuer_to_watchers(self, browser):
        browser.login().open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title': u'Abkl\xe4rung Fall Meier',
                      'Task Type': 'comment',
                      'Text': 'Lorem ipsum'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('hugo.boss')
        browser.css('#form-buttons-save').first.click()

        center = notification_center()
        resource = center.fetch_resource(self.dossier.listFolderContents()[0])
        subscriptions = resource.subscriptions

        self.assertItemsEqual(
            [(u'hugo.boss', TASK_RESPONSIBLE_ROLE),
             (u'test_user_1_', TASK_ISSUER_ROLE)],
            [(subscription.watcher.actorid, subscription.role)
             for subscription in subscriptions])

    @browsing
    def test_task_accepted(self, browser):
        task = create(Builder('task')
                      .titled(u'Abkl\xe4rung Fall Meier')
                      .having(responsible=TEST_USER_ID))

        browser.login().open(task)
        browser.css('#workflow-transition-task-transition-open-in-progress').first.click()
        browser.fill({'Response': u'Wird n\xe4chste Woche erledigt.'})
        browser.css('#form-buttons-save').first.click()

        # Ensure task accepted activity is fired only once.
        # Second activity is for task creation
        self.assertEqual(2, Activity.query.count())

        activity = Activity.query.order_by(desc(Activity.id)).first()
        self.assertEquals(u'task-transition-open-in-progress', activity.kind)
        self.assertEquals(u'Abkl\xe4rung Fall Meier', activity.title)
        self.assertEquals(
            u'Accepted by <a href="http://nohost/plone/@@user-details/test_user_1_">Test User (test_user_1_)</a>',
            activity.summary)
        self.assertEquals(u'Wird n\xe4chste Woche erledigt.', activity.description)

    @browsing
    def test_task_commented(self, browser):
        dossier = create(Builder('dossier'))
        task = create(Builder('task')
                      .within(dossier)
                      .titled(u'Abkl\xe4rung Fall Meier')
                      .having(responsible=TEST_USER_ID))

        browser.login().visit(task, view="addcommentresponse")
        browser.fill({'Response': u'Wird n\xe4chste Woche erledigt.'})
        browser.find('Save').click()

        # Ensure task comment activity is fired only once.
        # Second activity is for task creation
        self.assertEqual(2, Activity.query.count())

        activity = Activity.query.order_by(desc(Activity.id)).first()
        self.assertEquals(u'task-commented', activity.kind)
        self.assertEquals(u'Abkl\xe4rung Fall Meier', activity.title)
        self.assertEquals(
            u'Commented by <a href="http://nohost/plone/@@user-details/test_user_1_">Test User (test_user_1_)</a>',
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

        activity = Activity.query.order_by(desc(Activity.id)).first()
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

        # Ensure task resolution activity is fired only once.
        # Second activity is for task creation
        self.assertEqual(2, Activity.query.count())

        activity = Activity.query.order_by(desc(Activity.id)).first()
        self.assertEquals(u'task-transition-in-progress-resolved', activity.kind)
        self.assertEquals(u'Abkl\xe4rung Fall Meier', activity.title)
        self.assertEquals(
            u'Resolved by <a href="http://nohost/plone/@@user-details/test_user_1_">Test User (test_user_1_)</a>', activity.summary)
        self.assertEquals(u'Ist erledigt.', activity.description)

    @browsing
    def test_task_skipped(self, browser):
        task = create(Builder('task')
                      .titled(u'Abkl\xe4rung Fall Meier')
                      .having(responsible=TEST_USER_ID)
                      .in_state('task-state-rejected'))

        alsoProvides(task, IFromSequentialTasktemplate)
        transaction.commit()

        browser.login().open(task)
        browser.css('#workflow-transition-task-transition-rejected-skipped').first.click()
        browser.fill({'Response': u'Wird \xfcbersprungen.'})
        browser.css('#form-buttons-save').first.click()

        # Ensure skip task activity is fired only once.
        # Second activity is for task creation
        self.assertEqual(2, Activity.query.count())

        activity = Activity.query.order_by(desc(Activity.id)).first()
        self.assertEquals(u'task-transition-rejected-skipped', activity.kind)
        self.assertEquals(u'Abkl\xe4rung Fall Meier', activity.title)
        self.assertEquals(
            u'Skipped by <a href="http://nohost/plone/@@user-details/test_user_1_">Test User (test_user_1_)</a>', activity.summary)
        self.assertEquals(u'Wird \xfcbersprungen.', activity.description)

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
            'New Deadline': '20.03.2016',
            'Response': u'nicht dring\xe4nd'}).save()

        # Ensure modifying deadline activity is fired only once.
        # Second activity is for task creation
        self.assertEqual(2, Activity.query.count())

        activity = Activity.query.order_by(desc(Activity.id)).first()
        self.assertEquals(u'task-transition-modify-deadline', activity.kind)
        self.assertEquals(u'Abkl\xe4rung Fall Meier', activity.title)
        self.assertEquals(
            'Deadline modified from 01.03.2015 to 20.03.2016 by'
            ' <a href="http://nohost/plone/@@user-details/test_user_1_">'
            'Test User (test_user_1_)</a>', activity.summary)
        self.assertEquals(u'nicht dring\xe4nd', activity.description)

    @browsing
    def test_adding_a_subtask_creates_activity(self, browser):
        task = create(Builder('task')
                      .titled(u'Abkl\xe4rung Fall Meier')
                      .having(responsible=u'hugo.boss',
                              deadline=date(2015, 03, 01))
                      .in_state('task-state-in-progress'))

        browser.login().open(task, view='++add++opengever.task.task')
        browser.fill({'Title': u'Abkl\xe4rung Fall Meier',
                      'Task Type': 'comment',
                      'Text': 'Lorem ipsum'})

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('hugo.boss')
        form.find_widget('Issuer').fill(u'hugo.boss')

        browser.css('#form-buttons-save').first.click()

        # Ensure adding subtask activity is fired only once.
        # Second activity is for task creation
        self.assertEqual(2, Activity.query.count())

        activity = Activity.query.order_by(desc(Activity.id)).first()
        self.assertEquals('task-added', activity.kind)
        self.assertEquals(u'Abkl\xe4rung Fall Meier', activity.title)
        self.assertEquals(u'New task opened by Test User', activity.summary)

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

        # Ensure adding document activity is fired only once.
        # Second activity is for task creation
        self.assertEqual(2, Activity.query.count())

        activity = Activity.query.order_by(desc(Activity.id)).first()
        self.assertEquals(u'transition-add-document', activity.kind)

    @browsing
    def test_delegate_activity(self, browser):
        task = create(Builder('task')
                      .titled(u'Abkl\xe4rung Fall Huber')
                      .having(responsible=u'hugo.boss',
                              deadline=date(2015, 07, 01))
                      .in_state('task-state-in-progress'))

        browser.login().open(task)
        browser.find('task-transition-delegate').click()
        # fill responsibles step
        form = browser.find_form_by_field('Responsibles')
        form.find_widget('Responsibles').fill(['org-unit-1:hugo.boss'])

        browser.find('Continue').click()
        # fill medatata step and submit
        browser.find('Save').click()

        # Ensure delegating activity is fired only once.
        # Second activity is for task creation
        self.assertEqual(2, Activity.query.count())

        activity = Activity.query.order_by(desc(Activity.id)).first()
        self.assertEquals('task-added', activity.kind)
        self.assertEquals(u'Abkl\xe4rung Fall Huber', activity.title)
        self.assertEquals(u'New task opened by Test User', activity.summary)


class TestTaskReassignActivity(IntegrationTestCase):

    features = ('activity', )

    def reassign(self, browser, responsible, response, user=None):
        if user is None:
            user = self.manager
        with self.login(user, browser):
            browser.open(self.task)
            browser.css('#workflow-transition-task-transition-reassign').first.click()
            browser.fill({'Response': response})
            form = browser.find_form_by_field('Responsible')
            form.find_widget('Responsible').fill(responsible)
            browser.css('#form-buttons-save').first.click()

    @browsing
    def test_properties(self, browser):
        self.reassign(browser, self.meeting_user, u'Bitte Abkl\xe4rungen erledigen.')

        activities = Activity.query.all()
        self.assertEqual(1, len(activities))

        reassign_activity = activities[-1]

        self.assertEquals(u'task-transition-reassign', reassign_activity.kind)
        self.assertEquals(u'Vertragsentwurf \xdcberpr\xfcfen', reassign_activity.title)
        self.assertEquals(u'Reassigned from <a href="http://nohost/plone/@@user-details/kathi.barfuss">'
                          u'B\xe4rfuss K\xe4thi (kathi.barfuss)</a> '
                          u'to <a href="http://nohost/plone/@@user-details/herbert.jager">'
                          u'J\xe4ger Herbert (herbert.jager)</a> by admin (admin)',
                          reassign_activity.summary)
        self.assertEquals(u'Bitte Abkl\xe4rungen erledigen.', reassign_activity.description)

    @browsing
    def test_reassign_message_does_not_include_user_when_he_is_old_responsible(self, browser):
        self.reassign(browser, self.meeting_user,
                      u'Bitte Abkl\xe4rungen erledigen.',
                      self.regular_user)

        activities = Activity.query.all()
        self.assertEqual(1, len(activities))

        reassign_activity = activities[-1]

        self.assertEquals(u'task-transition-reassign', reassign_activity.kind)
        self.assertEquals(u'Vertragsentwurf \xdcberpr\xfcfen', reassign_activity.title)
        self.assertEquals(u'Reassigned from <a href="http://nohost/plone/@@user-details/kathi.barfuss">'
                          u'B\xe4rfuss K\xe4thi (kathi.barfuss)</a> '
                          u'to <a href="http://nohost/plone/@@user-details/herbert.jager">'
                          u'J\xe4ger Herbert (herbert.jager)</a>',
                          reassign_activity.summary)
        self.assertEquals(u'Bitte Abkl\xe4rungen erledigen.', reassign_activity.description)

    @browsing
    def test_notifies_old_and_new_responsible(self, browser):
        self.reassign(browser, self.meeting_user, u'Bitte Abkl\xe4rungen erledigen.')

        activities = Activity.query.all()
        self.assertEqual(1, len(activities))

        reassign_activity = activities[-1]

        self.assertItemsEqual(
            [self.regular_user.getId(), self.meeting_user.getId()],
            [notes.userid for notes in reassign_activity.notifications])

    @browsing
    def test_removes_old_responsible_from_watchers_list(self, browser):
        self.reassign(browser, self.meeting_user, u'Bitte Abkl\xe4rungen erledigen.')

        self.login(self.regular_user, browser)
        resource = notification_center().fetch_resource(self.task)
        create_session().refresh(resource)
        subscriptions = resource.subscriptions

        self.assertItemsEqual(
            [(u'herbert.jager', TASK_RESPONSIBLE_ROLE)],
            [(sub.watcher.actorid, sub.role) for sub in subscriptions])

    @browsing
    def test_handles_reassign_to_the_same_user_correctly(self, browser):
        # add additional org_unit
        org_unit = self.add_additional_org_unit()
        org_unit.users_group.users.append(User.get(self.regular_user.id))

        self.login(self.regular_user, browser)

        # manually register watchers
        center = notification_center()
        center.add_task_responsible(self.task, self.task.responsible)
        center.add_task_issuer(self.task, self.task.issuer)

        self.reassign(browser, self.regular_user, u'Bitte Abkl\xe4rungen erledigen.')

        resource = notification_center().fetch_resource(self.task)
        create_session().refresh(resource)
        subscriptions = resource.subscriptions

        self.assertItemsEqual(
            [(self.regular_user.id, TASK_RESPONSIBLE_ROLE),
             (self.dossier_responsible.id, TASK_ISSUER_ROLE)],
            [(sub.watcher.actorid, sub.role) for sub in subscriptions])

    @browsing
    def test_notifies_only_new_responsible_per_mail(self, browser):
        process_mail_queue()
        Mailing(self.portal).reset()

        self.reassign(browser, self.meeting_user, u'Bitte Abkl\xe4rungen erledigen.')
        process_mail_queue()

        self.assertEqual(1, len(Mailing(self.portal).get_messages()))

        mail = email.message_from_string(Mailing(self.portal).pop())
        self.assertEquals(
            'herbert.jager@gever.local', get_header(mail, 'To'))


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

        self.center.add_task_responsible(self.predecessor, 'peter.meier')
        self.center.add_task_issuer(self.predecessor, 'james.meier')
        self.center.add_watcher_to_resource(
            self.predecessor, 'hugo.boss', WATCHER_ROLE)

    def tearDown(self):
        super(TestSuccesssorHandling, self).tearDown()
        process_mail_queue()
        Mailing(self.layer['portal']).tear_down()

    def test_when_accepting_task_with_successor_responsible_watcher_gets_moved_from_predecessor_to_successsor(self):
        successor = accept_task_with_successor(
            self.dossier, self.predecessor.oguid.id, u'Ok.')

        predecessor_resource = self.center.fetch_resource(self.predecessor)
        successor_resource = self.center.fetch_resource(successor)

        self.assertItemsEqual(
            [(u'james.meier', u'task_issuer'),
             (u'hugo.boss', u'regular_watcher')],
            [(subscription.watcher.actorid, subscription.role)
             for subscription in predecessor_resource.subscriptions])

        self.assertItemsEqual(
            [(u'peter.meier', u'task_responsible')],
            [(subscription.watcher.actorid, subscription.role)
             for subscription in successor_resource.subscriptions])


class TestTaskReminderActivity(IntegrationTestCase):

    features = ('activity', )

    def test_activity_attributes(self):
        self.login(self.regular_user)
        TaskReminderActivity(self.task.get_sql_object(), self.request).record(
            self.dossier_responsible.getId())

        activity = Activity.query.first()

        self.assertEquals('task-reminder', activity.kind)
        self.assertEquals('Task reminder', activity.label)
        self.assertEquals(self.task.title, activity.title)
        self.assertEqual(SYSTEM_ACTOR_ID, activity.actor_id)
        self.assertEquals(u'Deadline is on Nov 01, 2016', activity.summary)
