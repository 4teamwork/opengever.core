from datetime import date
from datetime import timedelta
from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.base.actor import InboxActor
from opengever.testing import FunctionalTestCase
from opengever.testing import MEMORY_DB_LAYER
from sqlalchemy.exc import IntegrityError
from unittest2 import TestCase
from zope.globalrequest import getRequest
from zope.i18n.locales import locales
import transaction


class TestGlobalindexTaskDeadlineLabel(FunctionalTestCase):

    def setUp(self):
        super(TestGlobalindexTaskDeadlineLabel, self).setUp()
        # we wan't to test against a real locale, not the stupid default locale
        getRequest()._locale = locales.getLocale('de', 'ch')

    def test_deadline_label_returns_span_tag_with_formated_date(self):
        task = create(Builder('globalindex_task').having(
            int_id=12345, deadline=date(2512, 10, 25),
            review_state='task-state-open'))

        self.assertEquals('<span>25.10.2512</span>', task.get_deadline_label())

    def test_deadline_label_returns_long_format_when_specified(self):
        task = create(Builder('globalindex_task').having(
            int_id=12345, deadline=date(2512, 10, 25),
            review_state='task-state-open'))

        self.assertEquals('<span>25. Oktober 2512</span>',
                          task.get_deadline_label(format="long"))

    def test_deadline_label_contains_overdue_css_class_for_overdued_tasks(self):
        deadline = date.today() - timedelta(days=10)
        overdue = create(Builder('globalindex_task').having(deadline=deadline))

        self.assertEquals(
            '<span class="task-overdue">{}</span>'.format(deadline.strftime('%d.%m.%Y')),
            overdue.get_deadline_label())

    def test_deadline_returns_empty_string_for_tasks_without_a_deadline(self):
        task = create(Builder('globalindex_task'))

        self.assertEquals('', task.get_deadline_label())

    def test_get_deadline_label_for_future_labels(self):
        tomorrow = date.today() + timedelta(days=1)
        task = create(Builder('globalindex_task')
                      .having(int_id=1, deadline=tomorrow))

        self.assertEqual(
            '<span>{}</span>'.format(tomorrow.strftime('%d.%m.%Y')),
            task.get_deadline_label())

    def test_get_deadline_label_is_empty_when_no_deadline_is_set(self):
        task = create(Builder('globalindex_task')
                      .having(deadline=None))
        self.assertEqual('', task.get_deadline_label())

    def test_get_deadline_label_is_overdue_for_past_dates(self):
        yesterday = date.today() - timedelta(days=1)
        task = create(Builder('globalindex_task')
                      .having(int_id=1, deadline=yesterday))

        self.assertEqual(
            '<span class="task-overdue">{}</span>'.format(
                yesterday.strftime('%d.%m.%Y')),
            task.get_deadline_label())


class TestGlobalindexTask(TestCase):

    layer = MEMORY_DB_LAYER

    def test_task_representation(self):
        task1 = create(Builder('globalindex_task')
                       .having(admin_unit_id='afi', int_id=1234))

        self.assertEquals('<Task 1234@afi>', repr(task1))

    def test_predecessor_successor_relation(self):
        task1 = create(Builder('globalindex_task').having(int_id=1))
        task2 = create(Builder('globalindex_task').having(int_id=2))
        task2.predecessor = task1

        self.assertEquals([task2, ], task1.successors)

    def test_mulitple_successors(self):
        task1 = create(Builder('globalindex_task').having(int_id=1))
        task2 = create(Builder('globalindex_task').having(int_id=2))
        task3 = create(Builder('globalindex_task').having(int_id=3))

        task2.predecessor = task1
        task3.predecessor = task1

        self.assertEquals([task2, task3], task1.successors)

    def test_successor_is_not_inherited_when_chain_linking(self):
        task1 = create(Builder('globalindex_task').having(int_id=1))
        task2 = create(Builder('globalindex_task').having(int_id=2))
        task3 = create(Builder('globalindex_task').having(int_id=3))

        task2.predecessor = task1
        task3.predecessor = task2

        self.assertEquals([task2], task1.successors)
        self.assertEquals([task3], task2.successors)

    def test_is_successor(self):
        predecessor = create(Builder('globalindex_task').having(int_id=1))

        task_without_pred = create(Builder('globalindex_task').having(int_id=3))
        self.assertFalse(task_without_pred.is_successor)

        task_with_pred = create(Builder('globalindex_task').having(int_id=2))
        task_with_pred.predecessor = predecessor
        self.assertTrue(task_with_pred.is_successor)

    def test_unique_id(self):
        create(Builder('globalindex_task')
               .having(admin_unit_id='afi', int_id=1234))

        with self.assertRaises(IntegrityError):
            create(Builder('globalindex_task')
                           .having(admin_unit_id='afi', int_id=1234))
            transaction.commit()

        transaction.abort()

    def test_is_forwarding(self):
        forwarding = create(Builder('globalindex_task')
                       .having(int_id=1, task_type='forwarding_task_type'))
        task = create(Builder('globalindex_task')
               .having(int_id=2, task_type='direct-execution'))

        self.assertTrue(forwarding.is_forwarding)
        self.assertFalse(task.is_forwarding)

    def test_is_overdue_compare_deadline_with_today(self):
        early = create(Builder('globalindex_task').having(
            deadline=date.today() + timedelta(days=10)))
        overdue = create(Builder('globalindex_task').having(
            int_id=12346, deadline=date.today() - timedelta(days=10)))

        self.assertFalse(early.is_overdue)
        self.assertTrue(overdue.is_overdue)

    def test_is_overdue_respect_overdue_independent_states(self):
        overdue_date = date.today() - timedelta(days=10)

        closed = create(Builder('globalindex_task')
                        .having(int_id=1, deadline=overdue_date,
                                review_state='task-state-tested-and-closed'))
        cancelled = create(Builder('globalindex_task')
                           .having(int_id=2, deadline=overdue_date,
                                   review_state='task-state-cancelled'))
        resolved = create(Builder('globalindex_task')
                          .having(int_id=3, deadline=overdue_date,
                                  review_state='task-state-resolved'))
        rejected = create(Builder('globalindex_task')
                          .having(int_id=4, deadline=overdue_date,
                                  review_state='task-state-rejected'))
        closed_forwarding = create(Builder('globalindex_task')
                                   .having(int_id=5, deadline=overdue_date,
                                           task_type='forwarding',
                                           review_state='forwarding-state-closed'))

        self.assertFalse(closed.is_overdue)
        self.assertFalse(cancelled.is_overdue)
        self.assertFalse(resolved.is_overdue)
        self.assertFalse(rejected.is_overdue)
        self.assertFalse(closed_forwarding.is_overdue)

    def test_responsible_actor(self):
        admin_unit = create(Builder('admin_unit'))
        org_unit = create(Builder('org_unit').id('rr')
                          .having(admin_unit=admin_unit))
        task = create(Builder('globalindex_task')
                      .having(responsible='inbox:rr'))

        responsible_actor = task.responsible_actor

        self.assertTrue(isinstance(responsible_actor, InboxActor))
        self.assertEqual(org_unit, responsible_actor.org_unit)

    def test_issuer_actor(self):
        admin_unit = create(Builder('admin_unit'))
        org_unit = create(Builder('org_unit').id('rr')
                          .having(admin_unit=admin_unit))
        task = create(Builder('globalindex_task').having(issuer='inbox:rr'))

        issuer_actor = task.issuer_actor

        self.assertTrue(isinstance(issuer_actor, InboxActor))
        self.assertEqual(org_unit, issuer_actor.org_unit)

    def test_absolute_url_returns_the_absolute_url_of_the_plone_task(self):
        create(Builder('admin_unit').id(u'client1'))
        task = create(Builder('globalindex_task').having(admin_unit_id="client1",
                                                         physical_path="path/to/task"))

        self.assertEqual(task.absolute_url(),
                         u'http://example.com/public/path/to/task')

    def test_absolute_url_returns_an_empty_string_if_no_admin_unit_is_available(self):
        task = create(Builder('globalindex_task')
                      .having(admin_unit_id='not-existing'))

        self.assertEqual(task.absolute_url(), '')
