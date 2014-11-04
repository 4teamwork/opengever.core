from DateTime.DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from opengever.base.tests.byline_base_test import TestBylineBase
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import transaction


class TestTaskByline(TestBylineBase):

    use_default_fixture = False

    def setUp(self):
        super(TestTaskByline, self).setUp()
        self.intids = getUtility(IIntIds)

        self.user, self.org_unit, self.admin_unit = create(
            Builder('fixture')
            .with_user()
            .with_org_unit()
            .with_admin_unit(abbreviation='c1'))

        create(Builder('fixture').with_hugo_boss())

        self.task = create(Builder('task')
               .in_state('task-state-open')
               .having(responsible='hugo.boss',
                       filing_no='OG-Amt-2013-5'))

        self.task.creation_date = DateTime(2011, 8, 10, 20, 10)
        self.task.setModificationDate(DateTime(2011, 8, 11, 20, 10))
        transaction.commit()
        self.browser.open(self.task.absolute_url())

    def test_task_byline_responsible_display(self):
        responsible = self.get_byline_value_by_label('by:')
        self.assertEquals('Boss Hugo (hugo.boss)', responsible.text_content().strip())

    def test_dossier_byline_responsible_is_linked_to_user_details(self):
        responsible = self.get_byline_value_by_label('by:')
        self.assertEqual('http://nohost/plone/@@user-details/hugo.boss',
                         responsible.get('href'))

    def test_task_byline_state_display(self):
        state = self.get_byline_value_by_label('State:')
        self.assertEquals('task-state-open', state.text_content())

    def test_task_byline_start_date_display(self):
        start_date = self.get_byline_value_by_label('created:')
        self.assertEquals('Aug 10, 2011 08:10 PM', start_date.text_content())

    def test_task_byline_modification_date_display(self):
        start_date = self.get_byline_value_by_label('last modified:')
        self.assertEquals('Aug 11, 2011 08:10 PM', start_date.text_content())

    def test_dossier_byline_sequence_number_display_is_prefixed_with_admin_unit_abbreviation(self):
        seq_number = self.get_byline_value_by_label('Sequence Number:')
        self.assertEquals('c1 1', seq_number.text_content())
