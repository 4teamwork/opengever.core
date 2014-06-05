from ftw.builder import Builder
from ftw.builder import create
from opengever.globalindex.interfaces import ITaskQuery
from opengever.task.adapters import IResponseContainer
from opengever.task.interfaces import IDeadlineModifier
from opengever.task.interfaces import ISuccessorTaskController
from opengever.testing import FunctionalTestCase
from plone.app.testing import TEST_USER_ID
from zExceptions import Unauthorized
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import datetime


class TestDeadlineModificationForm(FunctionalTestCase):

    use_browser = True

    def setUp(self):
        super(TestDeadlineModificationForm, self).setUp()
        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

    def _change_deadline(self, task, new_deadline, text=u''):
        self.browser.open('%s/modify_deadline' % task.absolute_url())
        self.browser.fill({
            'New Deadline': new_deadline.strftime('%m/%d/%y'),
            'Response': text})
        self.browser.click('Save')

    def test_task_deadline_is_updated_when_set_to_a_valid_date(self):
        task = create(Builder('task')
                      .having(issuer=TEST_USER_ID, deadline=datetime.date(2013, 1, 1)))

        new_deadline = datetime.date(2013, 10, 1)

        self.browser.open('%s/modify_deadline' % task.absolute_url())
        self.browser.fill({
            'New Deadline': new_deadline.strftime('%m/%d/%y'), })
        self.browser.click('Save')

        self.assertEquals(task.deadline, datetime.date(2013, 10, 1))
        self.assertPageContains('Deadline successfully changed.')

    def test_raise_invalidation_error_when_new_deadline_is_the_current_one(self):
        current_deadline = datetime.date(2013, 1, 1)
        task = create(Builder('task')
                      .having(issuer=TEST_USER_ID, deadline=current_deadline))

        self.browser.open('%s/modify_deadline' % task.absolute_url())
        self.browser.fill({
            'New Deadline': current_deadline.strftime('%m/%d/%y'), })
        self.browser.click('Save')

        self.browser.assert_url('%s/modify_deadline' % task.absolute_url())
        self.assertPageContains('The given deadline, is the current one.')

    def test_deadline_is_updated_also_in_globalindex(self):
        task = create(Builder('task')
                      .having(issuer=TEST_USER_ID, deadline=datetime.date(2013, 1, 1)))

        self._change_deadline(task, datetime.date(2013, 10, 1), '')

        query = getUtility(ITaskQuery)
        intids = getUtility(IIntIds)

        sql_task = query.get_task(intids.getId(task), 'client1')
        self.assertEquals(sql_task.deadline, datetime.date(2013, 10, 1))

    def test_according_response_is_created_when_modify_deadline(self):
        task = create(Builder('task')
                     .having(issuer=TEST_USER_ID, deadline=datetime.date(2013, 1, 1)))

        self._change_deadline(task, datetime.date(2013, 10, 1), 'Lorem Ipsum')
        container = IResponseContainer(task)
        response = container[-1]

        self.assertEquals('Lorem Ipsum', response.text)
        self.assertEquals(TEST_USER_ID, response.creator)
        self.assertEquals(
            [{'after': datetime.date(2013, 10, 1),
              'id': 'deadline',
              'name': u'label_deadline',
              'before': datetime.date(2013, 1, 1)}],
            response.changes)

    def test_successor_is_also_updated_when_modify_predecessors_deadline(self):
        predecessor = create(Builder('task')
                             .having(issuer=TEST_USER_ID,
                                     deadline=datetime.date(2013, 1, 1)))
        succesor = create(Builder('task')
                          .having(issuer=TEST_USER_ID,
                                  deadline=datetime.date(2013, 1, 1)))

        ISuccessorTaskController(succesor).set_predecessor(
            ISuccessorTaskController(predecessor).get_oguid())

        self._change_deadline(
            predecessor, datetime.date(2013, 10, 1), 'Lorem Ipsum')

        self.assertEquals(succesor.deadline, datetime.date(2013, 10, 1))


class TestDeadlineModifierController(FunctionalTestCase):

    def setUp(self):
        super(TestDeadlineModifierController, self).setUp()
        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

    def test_modify_is_allowed_for_issuer_on_a_open_task(self):
        task = create(Builder('task').having(issuer=TEST_USER_ID))

        self.assertTrue(
            task.restrictedTraverse('is_deadline_modification_allowed')())

    def test_modify_is_allowed_for_issuer_on_a_in_progress_task(self):
        task = create(Builder('task')
                      .having(issuer=TEST_USER_ID, responsible=TEST_USER_ID)
                      .in_progress())

        self.assertTrue(
            task.restrictedTraverse('is_deadline_modification_allowed')())

    def test_modify_is_allowed_for_a_inbox_group_user_when_inbox_is_issuer(self):
        task = create(Builder('task')
                      .having(issuer='inbox:client1', responsible=TEST_USER_ID)
                      .in_progress())

        self.assertTrue(
            task.restrictedTraverse('is_deadline_modification_allowed')())

    def test_modify_is_allowed_for_admin_on_a_open_task(self):
        self.grant('Administrator')

        task = create(Builder('task')
                      .having(issuer='hugo.boss'))

        self.assertTrue(
            task.restrictedTraverse('is_deadline_modification_allowed')())

    def test_modify_is_allowed_for_admin_on_a_in_progress_task(self):
        self.grant('Administrator')

        task = create(Builder('task')
                      .having(issuer='hugo.boss')
                      .in_progress())
        self.assertTrue(
            task.restrictedTraverse('is_deadline_modification_allowed')())


class RemoteDeadlineModifier(FunctionalTestCase):

    use_browser = True

    def setUp(self):
        super(RemoteDeadlineModifier, self).setUp()
        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

    def test_updating_deadline_of_the_task(self):
        task = create(Builder('task')
                      .having(issuer=TEST_USER_ID,
                              deadline=datetime.date(2013, 1, 1)))

        task.REQUEST.set('new_deadline', datetime.date(2013, 10, 1).toordinal())
        task.REQUEST.set('text', 'Lorem ipsum')
        task.unrestrictedTraverse('remote_deadline_modifier')()

        self.assertEquals(task.deadline, datetime.date(2013, 10, 1))

    def test_raise_type_error_when_updating_view_with_missing_deadline(self):
        task = create(Builder('task')
                      .having(issuer=TEST_USER_ID,
                              deadline=datetime.date(2013, 1, 1)))

        task.REQUEST.set('text', 'Lorem Ipsum')
        with self.assertRaises(TypeError):
            task.unrestrictedTraverse('remote_deadline_modifier')()

    def test_according_response_is_added_when_modify_deadline(self):
        task = create(Builder('task')
                      .having(issuer=TEST_USER_ID,
                              deadline=datetime.date(2013, 1, 1)))

        task.REQUEST.set('new_deadline', datetime.date(2013, 10, 1).toordinal())
        task.REQUEST.set('text', 'Lorem Ipsum')
        task.unrestrictedTraverse('remote_deadline_modifier')()

        container = IResponseContainer(task)
        response = container[-1]

        self.assertEquals('Lorem Ipsum', response.text)
        self.assertEquals(TEST_USER_ID, response.creator)
        self.assertEquals(
            [{'after': datetime.date(2013, 10, 1),
              'id': 'deadline',
              'name': u'label_deadline',
              'before': datetime.date(2013, 1, 1)}],
            response.changes)


class TestDeadlineModifier(FunctionalTestCase):

    def setUp(self):
        super(TestDeadlineModifier, self).setUp()
        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture').with_all_unit_setup())

    def test_raise_unauthorized_when_mofication_is_not_allowed(self):
        task = create(Builder('task')
                      .having(issuer='hugo.boss',
                              deadline=datetime.date(2013, 1, 1)))

        with self.assertRaises(Unauthorized):
            IDeadlineModifier(task).modify_deadline(
                datetime.date(2013, 10, 1), 'changed deadline')
