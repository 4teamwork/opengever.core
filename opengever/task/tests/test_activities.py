from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity import Activity
from opengever.testing import FunctionalTestCase


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

        # XXX should use a better assertion like the ftw.testbrowser table
        # dict representation
        self.assertEquals(
            u'<table><tbody>'
            u'<tr><th>Task title</th><td>Abkl\xe4rung Fall Meier</td></tr>'
            u'<tr><th>Deadline</th><td>2015-02-12</td></tr>'
            u'<tr><th>Task type</th><td>To comment</td></tr>'
            u'<tr><th>Dossier title</th><td>Dossier XY</td></tr>'
            u'<tr><th>Text</th><td>Lorem ipsum</td></tr>'
            u'</tbody></table>',
            activity.description)
