from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity import Activity
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestActivityDescriptions(FunctionalTestCase):

    def setUp(self):
        super(TestActivityDescriptions, self).setUp()
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
                      'Text': 'Lorem ipsum',})
        browser.css('#form-buttons-save').first.click()

        activity = Activity.query.first()
        self.assertEquals('task-added', activity.kind)
        self.assertEquals(u'Abkl\xe4rung Fall Meier', activity.title)
        self.assertEquals(u'New task added by Test User', activity.summary)

        # XXX should be a better assertion like the ftw.testbrowser table
        # dict representation
        expected = (u'<table><tbody>'
                    u'<tr><th>Task title</th><td>Abkl\xe4rung Fall Meier</td></tr>'
                    u'<tr><th>Deadline</th><td>2015-02-13</td></tr>'
                    u'<tr><th>Task type</th><td>To comment</td></tr>'
                    u'<tr><th>Dossier title</th><td>Dossier XY</td></tr>'
                    u'<tr><th>Text</th><td>Lorem ipsum</td></tr></tbody></table>')
        self.assertEquals(expected, activity.description)

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
