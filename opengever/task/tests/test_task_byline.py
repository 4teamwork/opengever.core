import transaction
from DateTime.DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from opengever.base.tests.byline_base_test import TestBylineBase
from opengever.testing import create_ogds_user
from opengever.testing import create_client
from opengever.testing import set_current_client_id
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class TestTaskByline(TestBylineBase):
    
    def setUp(self):
        super(TestTaskByline, self).setUp()
        
        self.intids = getUtility(IIntIds)
        
        create_client()
        set_current_client_id(self.portal)
        create_ogds_user('hugo.boss')

        self.task = create(Builder('task')
               .in_state('task-state-open')
               .having(responsible='hugo.boss',
                       filing_no='OG-Amt-2013-5'))

        self.task.creation_date = DateTime(2011, 8, 10, 20, 10)
        self.task.setModificationDate(DateTime(2011, 8, 11, 20, 10))
        transaction.commit()
        self.browser.open(self.task.absolute_url())
        
    def test_task_byline_icon_display(self):
        icon = self.get_byline_element_by_class('byline-icon')
        self.assertEquals('byline-icon contenttype-opengever-task-task',
                          icon.target.get('class'))

    def test_task_byline_responsible_display(self):
        responsible = self.get_byline_value_by_label('by:')
        self.assertEquals('Boss Hugo (hugo.boss)', responsible.text_content().strip())

    def test_task_byline_state_display(self):
        state = self.get_byline_value_by_label('State:')
        self.assertEquals('task-state-open', state.text_content())

    def test_task_byline_start_date_display(self):
        start_date = self.get_byline_value_by_label('created:')
        self.assertEquals('Aug 10, 2011 08:10 PM', start_date.text_content())

    def test_task_byline_modification_date_display(self):
        start_date = self.get_byline_value_by_label('last modified:')
        self.assertEquals('Aug 11, 2011 08:10 PM', start_date.text_content())
        
    def test_dossier_byline_sequence_number_display(self):
        seq_number = self.get_byline_value_by_label('Sequence Number:')
        self.assertEquals('OG 1', seq_number.text_content())
