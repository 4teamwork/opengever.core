from ftw.builder import Builder
from ftw.builder import create
from opengever.task.adapters import IResponseContainer
from opengever.testing import FunctionalTestCase
from opengever.testing import task2sqltask
from plone.app.testing import TEST_USER_ID


class TestAssignTask(FunctionalTestCase):

    use_browser = True

    def setUp(self):
        super(TestAssignTask, self).setUp()

        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

        self.james = create(Builder('ogds_user')
                            .in_group(self.org_unit.users_group())
                            .having(userid='james.bond',
                                    firstname='James',
                                    lastname='Bond'))

        self.task = create(Builder('task')
                           .having(responsible_client='client1',
                                   responsible=TEST_USER_ID))

    def test_do_nothing_when_responsible_has_not_changed(self):
        self.assign_task('Test', TEST_USER_ID, '')

        self.assertEquals(self.task.absolute_url(),
                          self.browser.url.strip('/'))

        self.assertIn(
            'No changes: same responsible selected',
            [aa.plain_text() for aa in self.browser.css('.portalMessage dd')])

    def test_responsible_client_and_transition_field_is_hidden(self):
        self.browser.open('%s/assign-task' % (self.task.absolute_url()))

        with self.assertRaises(LookupError):
            self.browser.getControl('Responsible Client')

    def test_updates_responsible(self):

        self.assign_task('James', 'james.bond', '')

        self.assertEquals('james.bond', self.task.responsible)
        self.assertEquals('james.bond',
                          task2sqltask(self.task).responsible)

    def test_adds_an_corresponding_response(self):
        self.assign_task('James', 'james.bond', 'Please make that for me.')

        response = IResponseContainer(self.task)[-1]

        self.assertEquals(
            [{'after': u'james.bond', 'id': 'responsible',
             'name': u'label_responsible', 'before': 'test_user_1_'}],
            response.changes)
        self.assertEquals('Please make that for me.', response.text)

    def assign_task(self, name, userid, response):
        self.browser.open(
            '%s/assign-task?form.widgets.transition=%s' % (
                self.task.absolute_url(), 'task-transition-reassign'))

        self.browser.getControl(
            name='form.widgets.responsible.widgets.query').value = name
        self.browser.click('form.widgets.responsible.buttons.search')
        self.browser.getControl(name='form.widgets.responsible:list').value=[userid]
        self.browser.fill({'Response': response})
        self.browser.click('Assign')
