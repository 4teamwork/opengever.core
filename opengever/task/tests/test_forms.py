from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.activity.model import Activity
from opengever.activity.model import Subscription
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID


class TestTaskEditForm(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ACTIVITY_LAYER

    def setUp(self):
        super(TestTaskEditForm, self).setUp()
        create(Builder('ogds_user')
               .id('peter.meier')
               .assign_to_org_units([self.org_unit])
               .having(firstname=u'Peter', lastname=u'Meier'))
        create(Builder('ogds_user')
               .id('james.meier')
               .assign_to_org_units([self.org_unit])
               .having(firstname=u'James', lastname=u'Meier'))

        self.dossier = create(Builder('dossier').titled(u'Dossier'))

    @browsing
    def test_edit_responsible_adds_reassign_response(self, browser):
        task = create(Builder('task')
                      .within(self.dossier)
                      .having(title=u'Test task',
                              task_type='comment',
                              responsible='peter.meier'))

        browser.login().open(task, view='edit')

        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('org-unit-1:james.meier')
        browser.find('Save').click()

        browser.open(task, view='tabbedview_view-overview')
        answer = browser.css('.answer')[0]
        self.assertEquals('answer reassign', answer.get('class'))
        self.assertEquals(
            [u'Reassigned from Meier Peter (peter.meier)'
             ' to Meier James (james.meier) by Test User (test_user_1_)'],
            answer.css('h3').text)

    @browsing
    def test_edit_responsible_records_activity(self, browser):
        browser.login().open(self.dossier, view='++add++opengever.task.task')
        browser.fill({'Title': u'Abkl\xe4rung Fall Meier',
                      'Task Type': 'comment',
                      'Text': 'Lorem ipsum'})
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('org-unit-1:peter.meier')

        browser.find('Save').click()

        browser.open(browser.context.get('task-1'), view='edit')
        form = browser.find_form_by_field('Responsible')
        form.find_widget('Responsible').fill('org-unit-1:james.meier')

        browser.find('Save').click()

        activity = Activity.query.order_by(Activity.created.desc()).first()
        self.assertEquals(u'task-transition-reassign', activity.kind)
        self.assertEquals(
            [(TEST_USER_ID, u'task_issuer'),
             (u'james.meier', u'task_responsible')],
            [(sub.watcher.actorid, sub.role) for sub in Subscription.query.all()])
